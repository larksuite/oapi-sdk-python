"""Extra sender tests: on_success hook + markdown table_mode forwarded."""

import json

import pytest

from lark_oapi.channel.config import MarkdownConverter, OutboundConfig
from lark_oapi.channel.outbound.sender import OutboundSender, SendDriver
from lark_oapi.channel.types import OutboundPost, OutboundText


def _driver():
    async def create_message(**kwargs):
        return {"code": 0, "data": {"message_id": "om_abc"}}

    async def reply_message(**kwargs):  # pragma: no cover - unused here
        return {"code": 0}

    return SendDriver(create_message=create_message, reply_message=reply_message)


@pytest.mark.asyncio
async def test_on_success_hook_fires_with_message_id():
    got = []
    s = OutboundSender(_driver())
    s._on_success = lambda mid: got.append(mid)
    r = await s.send(OutboundText(text="hi"), receive_id="oc_1")
    assert r.success
    assert got == ["om_abc"]


@pytest.mark.asyncio
async def test_on_success_hook_not_called_on_failure():
    async def create_fail(**kwargs):
        return {"code": 99991663, "msg": "token"}

    async def noop(**kwargs):
        return {"code": 0}

    got = []
    s = OutboundSender(SendDriver(create_message=create_fail, reply_message=noop))
    s._on_success = lambda mid: got.append(mid)
    r = await s.send(OutboundText(text="hi"), receive_id="oc_1")
    assert r.success is False
    assert got == []


@pytest.mark.asyncio
async def test_table_mode_forwarded_to_markdown():
    captured = []

    async def create_message(**kwargs):
        captured.append(kwargs)
        return {"code": 0, "data": {"message_id": "om_abc"}}

    async def noop(**kwargs):
        return {"code": 0}

    s = OutboundSender(
        SendDriver(create_message=create_message, reply_message=noop),
        OutboundConfig(markdown_converter=MarkdownConverter(table_mode="bullets")),
    )
    md = "| name | age |\n|---|---|\n| Alice | 30 |"
    await s.send(OutboundPost(markdown=md), receive_id="oc_1")
    body = json.loads(captured[0]["content"])
    zh = body["zh_cn"]  # Feishu API — content is unwrapped locale map.
    # bullets mode emits "• name: Alice · age: 30"
    assert any("Alice" in (run.get("text") or "") and "•" in (run.get("text") or "") for run in zh["content"][0])


@pytest.mark.asyncio
async def test_table_mode_off_preserves_raw_table_lines():
    captured = []

    async def create_message(**kwargs):
        captured.append(kwargs)
        return {"code": 0, "data": {"message_id": "om_abc"}}

    async def noop(**kwargs):
        return {"code": 0}

    s = OutboundSender(
        SendDriver(create_message=create_message, reply_message=noop),
        OutboundConfig(markdown_converter=MarkdownConverter(table_mode="off")),
    )
    md = "| a | b |\n|---|---|\n| 1 | 2 |"
    await s.send(OutboundPost(markdown=md), receive_id="oc_1")
    body = json.loads(captured[0]["content"])
    zh = body["zh_cn"]  # Feishu API — content is unwrapped locale map.
    flat = "".join(run.get("text") or "" for para in zh["content"] for run in para)
    assert "| a | b |" in flat
