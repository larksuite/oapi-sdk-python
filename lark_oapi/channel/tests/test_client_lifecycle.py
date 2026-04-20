"""Coverage for `_ChannelClient` lifecycle internals without touching the network.

The `start()` method is hard to exercise (opens a WS connection); but the
pieces it wires up — bg loop, scheduling, sent-message tracking, safety
pipeline construction, dispatcher building — are all testable in isolation.
"""

import asyncio
import threading
import time

import pytest

from lark_oapi.channel import FeishuChannel as _ChannelClient
from lark_oapi.channel.bot_identity import BotIdentity


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
    c._ensure_bg_loop()   # no-op
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


def test_bot_identity_accessor_before_resolve():
    c = _client()
    assert c.bot_identity is None


def test_resolve_bot_identity_persists_to_safety_pipeline(monkeypatch):
    """When identity resolves, it should propagate into the safety PolicyGate."""
    from lark_oapi.channel.bot_identity import fetch_bot_identity as _real

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
        # ``processor not found`` (TC-317 reproduced this on the WS path).
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
