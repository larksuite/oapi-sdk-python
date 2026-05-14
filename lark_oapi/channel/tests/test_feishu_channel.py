"""Tests for the Node-aligned FeishuChannel facade."""

from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel, RejectEvent
from lark_oapi.channel._coerce import (
    coerce_outbound as _coerce_outbound,
    coerce_send_opts as _coerce_send_opts,
    normalize_event_name as _normalize_event_name,
)
from lark_oapi.channel.types import (
    OutboundCard,
    OutboundFile,
    OutboundImage,
    OutboundPost,
    OutboundText,
    SendOpts,
    SendResult,
)


# ---- input coercion --------------------------------------------------------


def test_coerce_string_defaults_to_markdown():
    ob = _coerce_outbound("**hi**")
    assert isinstance(ob, OutboundPost) and ob.markdown == "**hi**"


def test_coerce_dict_inputs_by_key():
    assert isinstance(_coerce_outbound({"markdown": "hi"}), OutboundPost)
    assert isinstance(_coerce_outbound({"text": "hi"}), OutboundText)
    assert isinstance(_coerce_outbound({"post": {}}), OutboundPost)
    assert isinstance(_coerce_outbound({"card": {}}), OutboundCard)


def test_coerce_image_with_url():
    ob = _coerce_outbound({"image": {"source": "https://example.com/x.png"}})
    assert isinstance(ob, OutboundImage)
    assert ob.source.kind == "url"
    assert ob.source.url == "https://example.com/x.png"


def test_coerce_image_with_key():
    ob = _coerce_outbound({"image": {"source": "img_abcdef"}})
    assert isinstance(ob, OutboundImage)
    assert ob.source.kind == "key"
    assert ob.source.key == "img_abcdef"


def test_coerce_file_with_filename():
    ob = _coerce_outbound({"file": {"source": b"\x00\x01", "fileName": "x.pdf"}})
    assert isinstance(ob, OutboundFile) and ob.file_name == "x.pdf"


def test_coerce_send_opts_camel_and_snake():
    opts = _coerce_send_opts({"replyTo": "om_x", "reply_in_thread": True})
    assert opts.reply_to == "om_x" and opts.reply_in_thread is True


def test_coerce_send_opts_passthrough_sendopts():
    so = SendOpts(reply_to="om_y")
    assert _coerce_send_opts(so) is so


# ---- event name normalization ----------------------------------------------


def test_event_name_aliases_collapse_to_node_names():
    assert _normalize_event_name("interaction") == "cardAction"
    assert _normalize_event_name("bot_added") == "botAdded"
    assert _normalize_event_name("bot_leave") == "botLeave"
    assert _normalize_event_name("message_read") == "messageRead"


# ---- FeishuChannel.on / off / reject wiring --------------------------------


@pytest.fixture
def channel():
    c = FeishuChannel(app_id="cli_test", app_secret="s")
    return c


def test_on_registers_and_unsubscribes(channel):
    calls = []

    def h(msg):
        calls.append(msg)

    unsub = channel.on("message", h)
    # Handlers are stored as a list so multiple subscribers can co-exist.
    for fn in channel._handlers.get("message", []):
        fn(None)
    assert len(calls) == 1
    unsub()
    # The list is cleared and the key pruned on final unsubscribe.
    assert channel._handlers.get("message") is None


def test_on_appends_multiple_handlers(channel):
    # New semantics: on() appends rather than replacing. Aligns with node-sdk
    # and with the EventEmitter / pub-sub pattern Python users expect.
    calls = []
    channel.on("message", lambda m: calls.append("a"))
    channel.on("message", lambda m: calls.append("b"))
    for fn in channel._handlers.get("message", []):
        fn(None)
    assert calls == ["a", "b"]


def test_on_dict_form_registers_many(channel):
    got = {}

    channel.on({
        "message": lambda m: got.setdefault("m", 1),
        "cardAction": lambda e: got.setdefault("c", 1),
    })
    assert "message" in channel._handlers
    assert "cardAction" in channel._handlers


def test_reject_handler_receives_reject_event(channel):
    received = []
    channel.on("reject", lambda e: received.append(e))
    # Simulate safety pipeline emitting a reject
    channel._emit_reject(RejectEvent(
        message_id="om_x", chat_id="oc_1", sender_id="ou_s",
        reason="policy_no_mention",
    ))
    assert received[0].reason == "policy_no_mention"


# ---- send routing ----------------------------------------------------------


@pytest.mark.asyncio
async def test_send_markdown_string_uses_post_sender(channel):
    channel._sender = AsyncMock()  # type: ignore[attr-defined]
    channel._sender.send = AsyncMock(return_value=SendResult.ok(message_id="om_ok"))
    await channel.send("oc_123", "**hi**")
    call = channel._sender.send.call_args
    # OutboundPost was constructed
    sent_msg = call.args[0]
    assert isinstance(sent_msg, OutboundPost) and sent_msg.markdown == "**hi**"


@pytest.mark.asyncio
async def test_send_infers_receive_id_type_from_prefix(channel):
    channel._sender = AsyncMock()
    channel._sender.send = AsyncMock(return_value=SendResult.ok(message_id="om_ok"))
    await channel.send("ou_someone", {"text": "hi"})
    call = channel._sender.send.call_args
    assert call.kwargs["receive_id_type"] == "open_id"
    await channel.send("oc_group", {"text": "hi"})
    call = channel._sender.send.call_args
    assert call.kwargs["receive_id_type"] == "chat_id"


# ---- update_policy + get_policy --------------------------------------------


def test_update_policy_patches_live(channel):
    # Force bg loop + safety pipeline up
    channel._ensure_bg_loop()
    channel.update_policy(require_mention=False)
    assert channel.get_policy().require_mention is False
