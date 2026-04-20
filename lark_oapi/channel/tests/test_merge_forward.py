"""merge_forward expansion tests (success + failure + depth limit)."""

import json

import pytest

from lark_oapi.channel.normalize.merge_forward import MergeForwardExpander
from lark_oapi.channel.types import MergeForwardContent, TextContent


def _child(mid, text, sender_id="ou_a"):
    return {
        "message_id": mid,
        "msg_type": "text",
        "body": {"content": json.dumps({"text": text})},
        "sender": {"id": sender_id},
        "create_time": "100",
    }


@pytest.mark.asyncio
async def test_expand_success():
    async def fetch(mid):
        return {"data": {"items": [
            {"message_id": mid, "msg_type": "merge_forward", "body": {"content": "{}"}},
            _child("c1", "hello"),
            _child("c2", "world", sender_id="ou_b"),
        ]}}

    async def names(ids):
        return {i: f"Name-{i}" for i in ids}

    exp = MergeForwardExpander(fetch_message=fetch, resolve_names=names)
    res = await exp.expand("om_root")
    assert isinstance(res, MergeForwardContent)
    assert len(res.items) == 2
    assert res.items[0].sender_name == "Name-ou_a"
    assert isinstance(res.items[0].content, TextContent)
    assert res.items[0].content.text == "hello"


@pytest.mark.asyncio
async def test_expand_truncates():
    async def fetch(mid):
        return {"data": {"items": [
            {"message_id": mid, "msg_type": "merge_forward", "body": {"content": "{}"}},
            *[_child(f"c{i}", f"msg{i}") for i in range(10)],
        ]}}

    exp = MergeForwardExpander(fetch_message=fetch, max_items=3)
    res = await exp.expand("om_root")
    assert res.truncated is True
    assert len(res.items) == 3


@pytest.mark.asyncio
async def test_expand_error_on_fetch_failure():
    async def fetch(mid):
        raise RuntimeError("network down")

    exp = MergeForwardExpander(fetch_message=fetch)
    res = await exp.expand("om_root")
    assert res.loading is False
    assert res.error and "network down" in res.error
    assert res.items == []


@pytest.mark.asyncio
async def test_empty_payload_error():
    async def fetch(mid):
        return None

    exp = MergeForwardExpander(fetch_message=fetch)
    res = await exp.expand("om_root")
    assert res.error == "empty_payload"


@pytest.mark.asyncio
async def test_depth_limit():
    async def fetch(mid):
        return {"data": {"items": [
            {"message_id": mid, "msg_type": "merge_forward", "body": {"content": "{}"}},
        ]}}

    exp = MergeForwardExpander(fetch_message=fetch, max_depth=0)
    res = await exp.expand("om_root", depth=1)
    assert res.error == "max_depth_exceeded"
