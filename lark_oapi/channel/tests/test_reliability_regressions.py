"""Reliability regression tests for channel lifecycle behavior."""

from __future__ import annotations

import asyncio
import threading
from unittest.mock import patch

import pytest

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.errors import FeishuChannelError, FeishuChannelErrorCode
from lark_oapi.ws.exception import ClientException


def _channel() -> FeishuChannel:
    return FeishuChannel(app_id="cli_test", app_secret="sec")


# ---------------------------------------------------------------------------
# Invalid credentials must surface as NOT_CONNECTED
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_credentials_error_has_not_connected_code():
    """When the WS handshake fails because app_id/app_secret are invalid,
    the channel must raise ``FeishuChannelError`` with code
    ``NOT_CONNECTED``. Today it re-raises the raw ``ClientException`` from
    :mod:`lark_oapi.ws.client`, whose ``.code`` is an ``int`` upstream error
    code, not a :class:`FeishuChannelErrorCode`.
    """
    ch = _channel()

    # Force the WS handshake to fail the way an "invalid credential"
    # response from Feishu would (``_get_conn_url`` raises ClientException
    # synchronously inside ``WSClient.start``).
    def _bad_url(self):
        raise ClientException(1000040346, "app_id is invalid")

    raised: Exception | None = None
    with patch(
        "lark_oapi.ws.client.Client._get_conn_url",
        _bad_url,
    ):
        try:
            await asyncio.wait_for(ch.connect(), timeout=10)
        except Exception as e:
            raised = e
        finally:
            try:
                ch.stop()
            except Exception:
                pass

    assert raised is not None, "connect() with invalid credentials must raise"

    # Keep the public error shape stable: error.code is a
    # FeishuChannelErrorCode whose value equals "not_connected".
    assert isinstance(raised, FeishuChannelError), (
        f"expected FeishuChannelError, got {type(raised).__name__}: {raised!r}"
    )
    assert raised.code is FeishuChannelErrorCode.NOT_CONNECTED, (
        f"expected NOT_CONNECTED, got {raised.code!r}"
    )
    assert raised.code.value == "not_connected"


# ---------------------------------------------------------------------------
# Reconnect after graceful disconnect must rebuild ws_client
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_reconnect_after_disconnect_reinitializes_ws_client():
    """Lifecycle contract:

    1. ``await channel.connect()`` brings the channel up.
    2. ``await channel.disconnect()`` tears it down cleanly.
    3. A subsequent ``await channel.connect()`` must bring it back up —
       ``channel.ws_client`` should be a fresh non-None WSClient.

    Today step 3 short-circuits: ``stop()`` does not reset ``_started``,
    and ``connect()`` early-returns when ``_started`` is True, so
    ``ws_client`` stays ``None``.
    """
    ch = _channel()

    fake_ws_instances: list = []

    class _FakeWS:
        def __init__(self, *a, **kw):
            self._conn = object()
            self._stopped = False
            fake_ws_instances.append(self)

        def start(self) -> None:
            # Non-blocking start: the real WSClient.start() blocks on
            # run_until_complete(_select); we just want to observe that it
            # was created.
            return None

        def stop(self) -> None:
            self._stopped = True

    # Patch both the imported symbol in channel.py and keep fetch_bot_identity
    # fast so the sync start() doesn't stall.
    async def _no_identity(_cfg):
        return None

    with patch("lark_oapi.channel.channel.WSClient", _FakeWS), patch(
        "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_no_identity
    ):
        await ch.connect()
        assert ch.ws_client is not None, "first connect() must build a WSClient"
        first = ch.ws_client

        await ch.disconnect()
        # disconnect() is documented to tear down — ws_client may be None
        # here, that's expected.

        # The bug: this second connect() must rebuild the ws_client.
        await ch.connect()

    assert ch.ws_client is not None, (
        "connect() after disconnect() must rebuild ws_client — today stop() "
        "leaves _started=True and _shutdown set, so the second connect() "
        "short-circuits and ws_client stays None"
    )
    assert ch.ws_client is not first, (
        "reconnect must produce a fresh WSClient instance, not reuse the "
        "torn-down one"
    )

    # Tidy up regardless of pass/fail.
    try:
        ch.stop()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Reconnecting / reconnected events must be dispatched
# ---------------------------------------------------------------------------


def test_reconnecting_event_is_dispatched_on_ws_reconnect():
    """When the underlying WS transport reconnects, ``channel`` must fire
    ``reconnecting`` and ``reconnected`` events to user handlers.

    ``FeishuChannel`` defines ``_notify_reconnecting`` /
    ``_notify_reconnected`` and :data:`ChannelEventName` advertises both
    event names — but nothing in :mod:`lark_oapi.channel.channel` or in
    :class:`lark_oapi.ws.client.Client` ever *calls* those notifiers. So a
    user that does ``channel.on("reconnecting", h)`` will never see a
    callback, even when the underlying transport reconnects repeatedly.

    Reproducer: drive the real ``WSClient._reconnect`` path and assert the
    channel-level handler fires. It won't, because there is no hook wired
    between :class:`WSClient` and :class:`FeishuChannel`.
    """
    ch = _channel()
    reconnecting_seen = threading.Event()
    reconnected_seen = threading.Event()

    ch.on("reconnecting", lambda *_a, **_kw: reconnecting_seen.set())
    ch.on("reconnected", lambda *_a, **_kw: reconnected_seen.set())

    # Mimic the real transport lifecycle: build a WSClient that exposes the
    # ``on_reconnecting`` / ``on_reconnected`` observer hooks (fixed on the
    # real :class:`lark_oapi.ws.client.Client`). FeishuChannel is expected to
    # wire its internal notifiers onto these attributes at start() time.
    class _FakeWS:
        def __init__(self, *a, **kw):
            self._conn = object()
            # Default no-op — FeishuChannel.start() overrides these.
            self.on_reconnecting = lambda: None
            self.on_reconnected = lambda: None

        def start(self) -> None:
            return None

        def stop(self) -> None:
            return None

        async def _reconnect(self) -> None:
            # A faithful stand-in for lark_oapi.ws.client.Client._reconnect:
            # fire ``on_reconnecting`` before retrying, then fire
            # ``on_reconnected`` once a connect succeeds. The real client in
            # ws/client.py does exactly this after the 2.0 fix.
            self.on_reconnecting()
            self.on_reconnected()

    async def _no_identity(_cfg):
        return None

    with patch("lark_oapi.channel.channel.WSClient", _FakeWS), patch(
        "lark_oapi.channel.channel.fetch_bot_identity", side_effect=_no_identity
    ):
        ch.start()
        ws = ch.ws_client
        assert ws is not None

        # Drive a reconnect through the underlying transport.
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(ws._reconnect())
        finally:
            loop.close()

    try:
        assert reconnecting_seen.wait(1.0), (
            "after the underlying ws client reconnects, channel must fire "
            "'reconnecting' — today it doesn't, because WSClient._reconnect "
            "has no callback hook back into FeishuChannel and "
            "FeishuChannel._notify_reconnecting() is dead code"
        )
        assert reconnected_seen.wait(1.0), (
            "after the underlying ws client reconnects, channel must fire "
            "'reconnected'"
        )
    finally:
        try:
            ch.stop()
        except Exception:
            pass
