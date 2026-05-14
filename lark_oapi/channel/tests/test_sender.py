"""End-to-end tests for OutboundSender using a fake driver."""

import json
from typing import Any, Dict, List

import pytest

from lark_oapi.channel.config import OutboundConfig
from lark_oapi.channel.outbound.sender import OutboundSender, SendDriver
from lark_oapi.channel.types import (
    Identity,
    MediaSource,
    OutboundCard,
    OutboundImage,
    OutboundPost,
    OutboundText,
)


def make_driver(responses=None, upload_key="img_xx"):
    calls: List[Dict[str, Any]] = []
    responses = responses or []
    idx = 0

    async def create_message(**kwargs):
        calls.append({"op": "create", **kwargs})
        nonlocal idx
        if idx < len(responses):
            r = responses[idx]
            idx += 1
            return r
        return {"code": 0, "msg": "ok", "data": {"message_id": "om_new"}}

    async def reply_message(**kwargs):
        calls.append({"op": "reply", **kwargs})
        return {"code": 0, "msg": "ok", "data": {"message_id": "om_reply"}}

    async def upload_image(**kwargs):
        calls.append({"op": "upload_image", **{k: v for k, v in kwargs.items() if k != "data"}})
        return {"code": 0, "data": {"image_key": upload_key}}

    driver = SendDriver(
        create_message=create_message,
        reply_message=reply_message,
        upload_image=upload_image,
    )
    return driver, calls


@pytest.mark.asyncio
async def test_text_sends_as_text_msg():
    d, calls = make_driver()
    s = OutboundSender(d)
    r = await s.send(OutboundText(text="hello"), receive_id="oc_1")
    assert r.success is True
    assert r.message_id == "om_new"
    payload = json.loads(calls[0]["content"])
    assert payload == {"text": "hello"}
    assert calls[0]["msg_type"] == "text"


@pytest.mark.asyncio
async def test_text_with_mentions_prefix_at():
    d, calls = make_driver()
    s = OutboundSender(d)
    await s.send(
        OutboundText(text="hi", mentions=[Identity(open_id="ou_1", display_name="Alice")]),
        receive_id="oc_1",
    )
    body = json.loads(calls[0]["content"])
    assert '<at user_id="ou_1">Alice</at>' in body["text"]
    assert body["text"].endswith(" hi")


@pytest.mark.asyncio
async def test_reply_via_reply_to():
    d, calls = make_driver()
    s = OutboundSender(d)
    r = await s.send(OutboundText(text="hi"), reply_to="om_parent")
    assert r.success is True
    assert calls[0]["op"] == "reply"
    assert calls[0]["message_id"] == "om_parent"


@pytest.mark.asyncio
async def test_chunks_long_text():
    d, calls = make_driver()
    s = OutboundSender(d, OutboundConfig(text_chunk_limit=10, chunk_mode="none"))
    await s.send(OutboundText(text="a" * 25), receive_id="oc_1")
    # expect 3 chunks => 3 create_message calls
    create_calls = [c for c in calls if c["op"] == "create"]
    assert len(create_calls) == 3


@pytest.mark.asyncio
async def test_post_from_markdown_emits_post_msg():
    d, calls = make_driver()
    s = OutboundSender(d)
    r = await s.send(OutboundPost(markdown="**bold**"), receive_id="oc_1")
    assert r.success is True
    assert calls[0]["msg_type"] == "post"
    content = json.loads(calls[0]["content"])
    # Feishu API expects {zh_cn: {...}} directly — NO outer {"post": ...} wrapper.
    # Wrapping with "post" causes server error 230001 (invalid message content).
    assert "post" not in content
    zh = content["zh_cn"]
    assert zh["content"][0][0]["text"] == "bold"


@pytest.mark.asyncio
async def test_card_sends_as_interactive():
    d, calls = make_driver()
    s = OutboundSender(d)
    r = await s.send(OutboundCard(card={"schema": "2.0", "body": {"elements": []}}), receive_id="oc_1")
    assert r.success is True
    assert calls[0]["msg_type"] == "interactive"
    body = json.loads(calls[0]["content"])
    assert body["schema"] == "2.0"


@pytest.mark.asyncio
async def test_image_url_uploads_first():
    d, calls = make_driver()
    s = OutboundSender(d)
    # buffer source skips network entirely
    r = await s.send(
        OutboundImage(source=MediaSource(kind="buffer", buffer=b"png_bytes")),
        receive_id="oc_1",
    )
    assert r.success is True
    ops = [c["op"] for c in calls]
    assert ops[0] == "upload_image"
    assert ops[1] == "create"


@pytest.mark.asyncio
async def test_error_response_classified():
    d, calls = make_driver(responses=[{"code": 230002, "msg": "not exist"}])
    s = OutboundSender(d)
    r = await s.send(OutboundText(text="hi"), receive_id="oc_1")
    assert r.success is False
    assert r.error.code.value == "target_revoked"
    assert r.error.retryable is False


@pytest.mark.asyncio
async def test_send_failure_log_redacts_request_content(caplog):
    d, calls = make_driver(responses=[{"code": 230001, "msg": "bad"}])
    s = OutboundSender(d)

    await s.send(OutboundText(text="secret customer payload"), receive_id="oc_1")

    assert "secret customer payload" not in caplog.text
    assert "request_content=" not in caplog.text
    assert "request_content_len=" in caplog.text


@pytest.mark.asyncio
async def test_receive_id_type_auto_detected():
    d, calls = make_driver()
    s = OutboundSender(d)
    await s.send(OutboundText(text="hi"), receive_id="ou_user")
    assert calls[0]["receive_id_type"] == "open_id"
