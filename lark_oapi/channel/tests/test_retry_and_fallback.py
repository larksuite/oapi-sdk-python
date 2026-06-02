"""Retry / fallback tests for OutboundSender."""

import json
from typing import List

import pytest

from lark_oapi.channel.config import OutboundConfig
from lark_oapi.channel.errors import FeishuChannelErrorCode, SendError
from lark_oapi.channel.outbound.retry import with_retry
from lark_oapi.channel.outbound.sender import OutboundSender, SendDriver
from lark_oapi.channel.types import OutboundPost, OutboundText, SendResult


# ---- retry primitive ------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_success_on_second_attempt():
    attempts = []

    async def op(i):
        attempts.append(i)
        if i == 0:
            return SendResult.fail(SendError(code=FeishuChannelErrorCode.RATE_LIMITED, retryable=True))
        return SendResult.ok(message_id="om_ok")

    r = await with_retry(op, max_attempts=3, base_delay_ms=1, jitter=False)
    assert r.success and r.message_id == "om_ok"
    assert attempts == [0, 1]


@pytest.mark.asyncio
async def test_retry_stops_on_non_retryable():
    attempts = []

    async def op(i):
        attempts.append(i)
        return SendResult.fail(SendError(code=FeishuChannelErrorCode.FORMAT_ERROR, retryable=False))

    r = await with_retry(op, max_attempts=3, base_delay_ms=1, jitter=False)
    assert r.success is False
    assert attempts == [0]


@pytest.mark.asyncio
async def test_retry_exhausts_attempts():
    attempts = []

    async def op(i):
        attempts.append(i)
        return SendResult.fail(SendError(code=FeishuChannelErrorCode.RATE_LIMITED, retryable=True))

    r = await with_retry(op, max_attempts=3, base_delay_ms=1, jitter=False)
    assert r.success is False
    assert attempts == [0, 1, 2]


# ---- sender-level fallback ------------------------------------------------


def _driver(responses: List[dict]):
    idx = 0
    calls: List[dict] = []

    async def create_message(**kwargs):
        nonlocal idx
        calls.append({"op": "create", **kwargs})
        r = responses[idx] if idx < len(responses) else {"code": 0, "data": {"message_id": "om_ok"}}
        idx += 1
        return r

    async def reply_message(**kwargs):
        nonlocal idx
        calls.append({"op": "reply", **kwargs})
        r = responses[idx] if idx < len(responses) else {"code": 0, "data": {"message_id": "om_reply"}}
        idx += 1
        return r

    return SendDriver(create_message=create_message, reply_message=reply_message), calls


@pytest.mark.asyncio
async def test_format_error_post_downgrades_to_text():
    """POST rejected with 230099 → retry as plain text (post_to_plain_text extraction)."""
    d, calls = _driver([
        {"code": 230099, "msg": "invalid card"},  # initial post — retryable? no, but fallback triggers
    ])
    s = OutboundSender(d)
    s._retry_max_attempts = 1
    r = await s.send(OutboundPost(markdown="**hi**"), receive_id="oc_1")
    assert r.success is True
    # The fallback call should have msg_type=text
    text_calls = [c for c in calls if c.get("msg_type") == "text"]
    assert len(text_calls) == 1
    assert json.loads(text_calls[0]["content"])["text"]


@pytest.mark.asyncio
async def test_reply_target_gone_retries_as_fresh():
    d, calls = _driver([
        {"code": 230020, "msg": "target revoked"},  # reply hits revoked target
    ])
    s = OutboundSender(d)
    s._retry_max_attempts = 1
    r = await s.send(OutboundText(text="hi"), reply_to="om_dead", receive_id="oc_1")
    assert r.success is True
    ops = [c["op"] for c in calls]
    assert ops[0] == "reply"
    assert ops[1] == "create"  # fell back to fresh create


@pytest.mark.asyncio
async def test_transient_error_retries_once():
    d, calls = _driver([
        {"code": 11020, "msg": "rate limited"},
    ])
    s = OutboundSender(d)
    s._retry_max_attempts = 2
    s._retry_base_delay_ms = 1
    r = await s.send(OutboundText(text="hi"), receive_id="oc_1")
    assert r.success is True
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_long_text_splits_preserving_order_first_reply_only():
    d, calls = _driver([])
    s = OutboundSender(d, OutboundConfig(text_chunk_limit=10, chunk_mode="none"))
    s._retry_max_attempts = 1
    r = await s.send(OutboundText(text="a" * 25), reply_to="om_target", receive_id="oc_1")
    assert r.success is True
    assert calls[0]["op"] == "reply"  # first chunk replies
    for c in calls[1:]:
        assert c["op"] == "create"  # subsequent chunks are fresh
