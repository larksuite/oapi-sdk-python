"""Outbound share/sticker coercion plus error and reject event forwarding."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import (
    FeishuChannel,
    OutboundShareChat,
    OutboundShareUser,
    OutboundSticker,
)
from lark_oapi.channel._coerce import coerce_outbound
from lark_oapi.channel.safety import SafetyPipeline
from lark_oapi.channel.types import (
    Conversation,
    Identity,
    InboundMessage,
    SendError,
    TextContent,
)
from lark_oapi.channel.errors import FeishuChannelErrorCode, OutboundSendError


# ---------------------------------------------------------------------------
# Outbound share_chat / share_user / sticker coercion.
# ---------------------------------------------------------------------------


def test_coerce_share_chat_dict():
    out = coerce_outbound({"share_chat": {"chat_id": "oc_xyz"}})
    assert isinstance(out, OutboundShareChat)
    assert out.chat_id == "oc_xyz"


def test_coerce_share_chat_camelcase_and_string_shorthand():
    # camelCase key for cross-language JSON compatibility.
    assert coerce_outbound({"shareChat": {"chatId": "oc_cam"}}).chat_id == "oc_cam"
    # Bare string shorthand: ``{"share_chat": "oc_..."}`` → same thing.
    assert coerce_outbound({"share_chat": "oc_bare"}).chat_id == "oc_bare"


def test_coerce_share_user_dict():
    out = coerce_outbound({"share_user": {"user_id": "ou_xyz"}})
    assert isinstance(out, OutboundShareUser)
    assert out.user_id == "ou_xyz"


def test_coerce_share_user_accepts_open_id_alias():
    # On the wire Feishu calls this field ``user_id`` but Python users
    # usually hold an ``open_id`` in hand; both accepted for ergonomics.
    assert coerce_outbound({"share_user": {"open_id": "ou_open"}}).user_id == "ou_open"


def test_coerce_sticker_dict():
    out = coerce_outbound({"sticker": {"file_key": "img_key_123"}})
    assert isinstance(out, OutboundSticker)
    assert out.file_key == "img_key_123"


def test_coerce_sticker_string_shorthand():
    assert coerce_outbound({"sticker": "img_key_abc"}).file_key == "img_key_abc"


@pytest.mark.asyncio
async def test_send_share_chat_wire_format():
    """End-to-end: ``channel.send(to, {"share_chat": ...})`` must produce a
    Feishu ``msg_type=share_chat`` wire body with ``content={"chat_id": ...}``
    (JSON-encoded). Patch the sender's ``SendDriver`` directly — monkey-
    patching ``channel._driver.create_message`` as an instance attribute
    does NOT propagate because ``OutboundSender`` captured the bound
    method at construction time."""
    import json
    ch = FeishuChannel(app_id="cli_x", app_secret="s")
    ch._sender._driver.create_message = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 0, "data": {"message_id": "om_sent"}}
    )
    result = await ch.send("oc_target", {"share_chat": {"chat_id": "oc_src"}})
    assert result.success is True
    assert result.message_id == "om_sent"
    call = ch._sender._driver.create_message.call_args
    body = call.kwargs
    assert body["msg_type"] == "share_chat"
    assert json.loads(body["content"]) == {"chat_id": "oc_src"}


@pytest.mark.asyncio
async def test_send_sticker_wire_format():
    import json
    ch = FeishuChannel(app_id="cli_x", app_secret="s")
    ch._sender._driver.create_message = AsyncMock(
        return_value={"code": 0, "data": {"message_id": "om_sticker"}}
    )
    result = await ch.send("oc_target", {"sticker": {"file_key": "img_k"}})
    assert result.success is True
    call = ch._sender._driver.create_message.call_args
    body = call.kwargs
    assert body["msg_type"] == "sticker"
    assert json.loads(body["content"]) == {"file_key": "img_k"}


# ---------------------------------------------------------------------------
# on("error") receives send/stream failures.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_failure_forwarded_to_on_error():
    """When ``channel.send()`` returns a ``SendResult.fail(...)``, any
    handler registered via ``on("error", ...)`` must also see the error.
    The original ``SendResult`` is still returned to the caller — forwarding
    does not swallow."""
    ch = FeishuChannel(app_id="cli_x", app_secret="s")
    seen = []
    ch.on("error", lambda e: seen.append(e))

    # Driver returns a rate-limit code → sender retries + eventually returns
    # SendResult.fail(RATE_LIMITED, ...). Patch on the SendDriver seam the
    # sender actually captured.
    ch._sender._driver.create_message = AsyncMock(  # type: ignore[attr-defined]
        return_value={"code": 11020, "msg": "rate limited"}
    )
    # Tighten retry so the test is quick.
    ch._sender._config.retry.max_attempts = 1  # type: ignore[attr-defined]
    ch._sender._config.retry.base_delay_ms = 1  # type: ignore[attr-defined]

    result = await ch.send("oc_x", {"text": "hi"})
    assert result.success is False
    assert result.error is not None
    assert result.error.code == FeishuChannelErrorCode.RATE_LIMITED
    # Direct caller still sees the SendError dataclass via result.error.
    assert isinstance(result.error, SendError)
    # Forwarded — handlers receive an Exception subclass so generic
    # diagnostic tooling (logger.exception, traceback formatting, Sentry)
    # works uniformly. The original SendError is preserved at .send_error.
    assert len(seen) == 1
    assert isinstance(seen[0], OutboundSendError)
    assert isinstance(seen[0], Exception)
    assert seen[0].code == FeishuChannelErrorCode.RATE_LIMITED
    assert seen[0].send_error is result.error
    assert seen[0].retryable is True
    assert seen[0].raw_code == 11020


@pytest.mark.asyncio
async def test_send_raised_exception_forwarded_to_on_error():
    """Even exceptions raised synchronously during coerce (e.g. unknown
    input shape) must be forwarded before the re-raise."""
    ch = FeishuChannel(app_id="cli_x", app_secret="s")
    seen = []
    ch.on("error", lambda e: seen.append(e))

    with pytest.raises(TypeError):
        await ch.send("oc_x", {"no_such_key": "oops"})

    assert len(seen) == 1
    assert isinstance(seen[0], TypeError)


# ---------------------------------------------------------------------------
# RejectEvent emission on dedup / stale hits.
# ---------------------------------------------------------------------------


def _inbound(msg_id: str, *, create_time: int = 1_000_000_000_000) -> InboundMessage:
    return InboundMessage(
        id=msg_id,
        create_time=create_time,
        conversation=Conversation(chat_id="oc_x", chat_type="p2p"),
        sender=Identity(open_id="ou_sender"),
        content=TextContent(text="hi"),
    )


@pytest.mark.asyncio
async def test_duplicate_emits_reject_event():
    """Feeding the same message_id twice through SafetyPipeline's full
    tier must emit ``RejectEvent(reason="duplicate")`` on the second hit
    (before: silent drop).

    Disables the per-chat queue so the first ``push_message`` synchronously
    runs through handler → ``seen.add`` before returning — otherwise the
    dedup mark would be set inside a later batch flush and the second
    push wouldn't see it.
    """
    from lark_oapi.channel.config import ChatQueueConfig
    import time

    loop = asyncio.get_running_loop()
    rejects = []
    dispatched = []

    async def on_msg(m):
        dispatched.append(m)

    sp = SafetyPipeline(
        loop=loop,
        on_message=on_msg,
        on_reject=lambda e: rejects.append(e),
        queue_config=ChatQueueConfig(enabled=False),
    )
    msg = _inbound("om_dup", create_time=int(time.time() * 1000))
    await sp.push_message(msg)
    assert len(dispatched) == 1, "first push should dispatch"
    await sp.push_message(msg)  # duplicate
    assert any(
        r.reason == "duplicate" and r.message_id == "om_dup" for r in rejects
    ), f"expected a 'duplicate' RejectEvent, got {rejects}"


@pytest.mark.asyncio
async def test_stale_emits_reject_event():
    """A message with ``create_time`` older than the stale window must emit
    ``RejectEvent(reason="stale")`` (before: silent drop)."""
    loop = asyncio.get_running_loop()
    rejects = []
    sp = SafetyPipeline(
        loop=loop,
        on_message=lambda m: asyncio.sleep(0),
        on_reject=lambda e: rejects.append(e),
        stale_window_ms=1,  # almost everything counts as stale
    )
    # A create_time from well in the past → definitely stale.
    msg = _inbound("om_stale", create_time=1)
    await sp.push_message(msg)
    assert any(
        r.reason == "stale" and r.message_id == "om_stale" for r in rejects
    ), f"expected a 'stale' RejectEvent, got {rejects}"
