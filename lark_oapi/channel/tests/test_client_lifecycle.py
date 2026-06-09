"""Coverage for `_ChannelClient` lifecycle internals without touching the network.

The `start()` method is hard to exercise (opens a WS connection); but the
pieces it wires up — bg loop, scheduling, sent-message tracking, safety
pipeline construction, dispatcher building — are all testable in isolation.
"""

import asyncio
import threading
from unittest.mock import patch

import pytest

from lark_oapi.channel import FeishuChannel as _ChannelClient
from lark_oapi.channel.bot_identity import BotIdentity
from lark_oapi.channel.errors import FeishuChannelError, FeishuChannelErrorCode


def _client() -> _ChannelClient:
    return _ChannelClient(app_id="cli_test", app_secret="sec")


def test_build_does_not_spin_up_bg_loop():
    c = _client()
    assert c._bg_loop is None
    assert c._safety is None


def test_ensure_bg_loop_is_idempotent():
    c = _client()
    c._ensure_bg_loop()
    loop = c._bg_loop
    assert loop is not None
    assert c._safety is not None
    c._ensure_bg_loop()  # no-op
    assert c._bg_loop is loop


def test_schedule_runs_coroutine_on_bg_loop():
    c = _client()
    done = threading.Event()
    ran_on = {}

    async def task():
        ran_on["loop"] = asyncio.get_running_loop()
        done.set()

    c.schedule(task())
    assert done.wait(2.0), "coroutine never fired"
    assert ran_on["loop"] is c._bg_loop


def test_track_sent_message_bounded_lru():
    c = _client()
    c._sent_messages_max = 3
    c._track_sent_message("a")
    c._track_sent_message("b")
    c._track_sent_message("c")
    c._track_sent_message("d")  # evicts 'a'
    assert "a" not in c._sent_messages
    assert "d" in c._sent_messages


def test_track_sent_message_ignores_empty():
    c = _client()
    c._track_sent_message("")
    assert len(c._sent_messages) == 0


def test_track_sent_message_refreshes_on_touch():
    c = _client()
    c._sent_messages_max = 3
    c._track_sent_message("a")
    c._track_sent_message("b")
    c._track_sent_message("c")
    # Touch 'a' again — should stay even after next insert evicts oldest
    c._track_sent_message("a")
    c._track_sent_message("d")
    assert "a" in c._sent_messages


@pytest.mark.asyncio
async def test_start_background_returns_after_ws_ready_without_waiting_for_start_exit():
    c = _client()
    started = threading.Event()
    release = threading.Event()

    class _BlockingReadyWS:
        def __init__(self, *args, **kwargs):
            self._conn = None
            self._stopped = False

        def start(self):
            self._conn = object()
            started.set()
            release.wait(timeout=2.0)

        def stop(self):
            self._stopped = True
            release.set()

    async def _no_identity(_cfg):
        return None

    with patch("lark_oapi.channel.channel.WSClient", _BlockingReadyWS), patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_no_identity
    ):
        await asyncio.wait_for(c.start_background(timeout=1.0), timeout=1.0)
        assert started.is_set()
        assert c.is_ready is True
        assert c._start_future is not None
        assert c._start_future.done() is False

        await c.stop_background()
        assert c.is_ready is False


@pytest.mark.asyncio
async def test_start_background_propagates_not_connected_startup_failure():
    c = _client()

    class _FailingWS:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            raise RuntimeError("handshake failed")

    async def _no_identity(_cfg):
        return None

    with patch("lark_oapi.channel.channel.WSClient", _FailingWS), patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_no_identity
    ):
        with pytest.raises(FeishuChannelError) as exc:
            await c.start_background(timeout=1.0)

    assert exc.value.code is FeishuChannelErrorCode.NOT_CONNECTED


@pytest.mark.asyncio
async def test_stop_background_wakes_in_flight_start_background_waiter():
    c = _client()
    start_entered = threading.Event()
    release_start = threading.Event()

    class _BlockingNotReadyWS:
        def __init__(self, *args, **kwargs):
            self._conn = None

        def start(self):
            start_entered.set()
            release_start.wait(timeout=2.0)

        def stop(self):
            release_start.set()

    async def _identity(_cfg):
        return BotIdentity(open_id="ou_bot")

    with patch("lark_oapi.channel.channel.WSClient", _BlockingNotReadyWS), patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_identity
    ):
        start_task = asyncio.create_task(c.start_background(timeout=10.0))
        while not start_entered.wait(0.01):
            await asyncio.sleep(0.01)

        await c.stop_background()
        await asyncio.wait_for(start_task, timeout=1.0)

    assert c.is_ready is False
    assert c._started is False


@pytest.mark.asyncio
async def test_start_background_after_stop_waits_for_new_readiness(monkeypatch):
    c = _client()
    c.stop()
    loop = asyncio.get_running_loop()
    start_future = loop.create_future()
    submitted = threading.Event()

    def fake_run_in_executor(executor, fn):
        submitted.set()
        return start_future

    monkeypatch.setattr(loop, "run_in_executor", fake_run_in_executor)

    start_task = asyncio.create_task(c.start_background(timeout=1.0))
    while not submitted.wait(0.01):
        await asyncio.sleep(0.01)
    await asyncio.sleep(0.05)

    assert start_task.done() is False

    c._mark_ready()
    start_future.set_result(None)
    await asyncio.wait_for(start_task, timeout=1.0)


def test_stop_during_blocking_start_does_not_surface_late_ws_start_exception():
    c = _client()
    ready = threading.Event()
    release = threading.Event()
    errors = []

    class _LateFailingWS:
        def __init__(self, *args, **kwargs):
            self._conn = None

        def start(self):
            self._conn = object()
            ready.set()
            release.wait(timeout=2.0)
            raise RuntimeError("loop stopped during shutdown")

        def stop(self):
            return None

    async def _identity(_cfg):
        return BotIdentity(open_id="ou_bot")

    with patch("lark_oapi.channel.channel.WSClient", _LateFailingWS), patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_identity
    ):
        def run_start():
            try:
                c.start()
            except Exception as exc:
                errors.append(exc)

        t = threading.Thread(target=run_start)
        t.start()
        assert ready.wait(1.0)
        c.stop()
        release.set()
        t.join(timeout=2.0)

    assert not t.is_alive()
    assert errors == []
    assert c._started is False
    assert c.is_ready is False


def test_stop_during_pre_ws_start_prevents_late_ws_creation():
    c = _client()
    fetch_entered = threading.Event()
    release_fetch = threading.Event()
    ws_started = threading.Event()
    errors = []

    class _ShouldNotStartWS:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            ws_started.set()

    async def _slow_identity(_cfg):
        fetch_entered.set()
        await asyncio.get_running_loop().run_in_executor(None, release_fetch.wait)
        return BotIdentity(open_id="ou_bot")

    with patch("lark_oapi.channel.channel.WSClient", _ShouldNotStartWS), patch(
            "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_slow_identity
    ):
        def run_start():
            try:
                c.start()
            except Exception as exc:
                errors.append(exc)

        t = threading.Thread(target=run_start)
        t.start()
        assert fetch_entered.wait(1.0)
        stop_t = threading.Thread(target=c.stop)
        stop_t.start()
        release_fetch.set()
        t.join(timeout=2.0)
        stop_t.join(timeout=2.0)

    assert not t.is_alive()
    assert not stop_t.is_alive()
    assert errors == []
    assert ws_started.is_set() is False
    assert c.ws_client is None
    assert c._started is False
    assert c.is_ready is False


def test_stale_pre_ws_start_cannot_be_uncancelled_by_restart():
    c = _client()
    first_fetch_entered = threading.Event()
    second_fetch_entered = threading.Event()
    release_first_fetch = threading.Event()
    release_second_fetch = threading.Event()
    fetch_count = 0
    labels_by_thread = {}
    started_labels = []
    errors = []
    lock = threading.Lock()

    class _LabelledWS:
        def __init__(self, *args, **kwargs):
            self._conn = object()

        def start(self):
            with lock:
                started_labels.append(labels_by_thread.get(threading.get_ident()))

        def stop(self):
            return None

    def _slow_fetch():
        nonlocal fetch_count
        with lock:
            fetch_count += 1
            label = "first" if fetch_count == 1 else "second"
            labels_by_thread[threading.get_ident()] = label
        if label == "first":
            first_fetch_entered.set()
            release_first_fetch.wait(timeout=2.0)
        else:
            second_fetch_entered.set()
            release_second_fetch.wait(timeout=2.0)

    with patch("lark_oapi.channel.channel.WSClient", _LabelledWS), patch.object(
            c, "_fetch_bot_identity_sync", side_effect=_slow_fetch
    ):
        def run_start():
            try:
                c.start()
            except Exception as exc:
                errors.append(exc)

        first = threading.Thread(target=run_start)
        first.start()
        assert first_fetch_entered.wait(1.0)

        c.stop()

        second = threading.Thread(target=run_start)
        second.start()
        assert second_fetch_entered.wait(1.0)

        release_first_fetch.set()
        first.join(timeout=2.0)
        release_second_fetch.set()
        second.join(timeout=2.0)

    assert not first.is_alive()
    assert not second.is_alive()
    assert errors == []
    assert "first" not in started_labels
    assert "second" in started_labels


def test_bot_identity_accessor_before_resolve():
    c = _client()
    assert c.bot_identity is None


def test_resolve_bot_identity_persists_to_safety_pipeline(monkeypatch):
    """When identity resolves, it should propagate into the safety PolicyGate."""

    async def fake_fetch(config):
        return BotIdentity(open_id="ou_bot_xyz", name="Test Bot")

    c = _client()
    c._ensure_bg_loop()
    monkeypatch.setattr("lark_oapi.channel.channel.fetch_bot_identity", fake_fetch)
    fut = asyncio.run_coroutine_threadsafe(c.resolve_bot_identity(), c._bg_loop)
    identity = fut.result(timeout=2)
    assert identity.open_id == "ou_bot_xyz"
    assert c._bot_open_id == "ou_bot_xyz"
    # Safety gate's bot open id should also be set
    assert c._safety._policy._bot_open_id == "ou_bot_xyz"  # type: ignore[attr-defined]


def test_build_dispatcher_registers_required_events():
    """Dispatcher should have processors for all 5 event types we handle."""
    c = _client()
    c._ensure_bg_loop()
    dispatcher = c._build_dispatcher()
    keys = set(dispatcher._processorMap.keys())
    keys |= set(dispatcher._callback_processor_map.keys())
    expected = {
        "p2.im.message.receive_v1",
        "p2.card.action.trigger",
        "p2.im.message.reaction.created_v1",
        "p2.im.message.reaction.deleted_v1",
        "p2.im.chat.member.bot.added_v1",
        "p2.im.chat.member.bot.deleted_v1",
        "p2.im.message.message_read_v1",
        # drive comment-add has no typed SDK processor and the wire
        # payload may arrive under either schema (p1 callback envelope vs
        # p2 WS envelope). Register both so neither path logs
        # ``processor not found``.
        "p1.drive.notice.comment_add_v1",
        "p2.drive.notice.comment_add_v1",
    }
    missing = expected - keys
    assert not missing, f"dispatcher missing processors: {missing}"


def test_emit_reject_with_no_handler_only_logs(caplog):
    import logging

    from lark_oapi.channel.safety import RejectEvent

    c = _client()
    with caplog.at_level(logging.DEBUG, logger="lark_oapi"):
        c._emit_reject(RejectEvent(
            message_id="om_x", chat_id="oc_x", sender_id="ou_s", reason="policy_no_mention",
        ))
    # With no handler registered, _emit_reject must not raise. It may or may
    # not log anything depending on level, but it must at least not surface
    # through an uncaught exception.
    # (Previously this assertion ended with ``... or True`` which made it
    # vacuously pass; the intent was "tolerate missing log line while still
    # asserting no exception", which the ``with caplog.at_level`` + absence
    # of pytest raise already covers.)


def test_emit_reject_dispatches_to_registered_handler():
    from lark_oapi.channel.safety import RejectEvent

    c = _client()
    got = []
    c.on("reject", lambda e: got.append(e))
    c._emit_reject(RejectEvent(
        message_id="om_x", chat_id="oc_x", sender_id="ou_s", reason="policy_dm_disabled",
    ))
    assert len(got) == 1
    assert got[0].reason == "policy_dm_disabled"
