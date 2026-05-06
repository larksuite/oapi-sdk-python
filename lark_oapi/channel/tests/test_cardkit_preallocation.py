"""Cardkit preallocation API tests (node-aligned).

Covers :meth:`FeishuChannel.create_card_instance`,
:meth:`send_card_by_reference`, :meth:`update_card_element_content`,
:meth:`finish_streaming_card`.
"""

import json
from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.errors import FeishuChannelError


@pytest.fixture
def channel() -> FeishuChannel:
    return FeishuChannel(app_id="cli_x", app_secret="s")


@pytest.mark.asyncio
async def test_create_card_instance_returns_card_id(channel):
    channel._driver.cardkit_create = AsyncMock(
        return_value={"code": 0, "data": {"card_id": "AAQ_card_xyz"}}
    )
    cid = await channel.create_card_instance({"schema": "2.0"})
    assert cid == "AAQ_card_xyz"
    call = channel._driver.cardkit_create.await_args
    body = call.kwargs["body"]
    assert body["type"] == "card_json"
    assert json.loads(body["data"]) == {"schema": "2.0"}


@pytest.mark.asyncio
async def test_create_card_instance_failure_raises(channel):
    channel._driver.cardkit_create = AsyncMock(
        return_value={"code": 400, "msg": "bad spec"}
    )
    with pytest.raises(FeishuChannelError):
        await channel.create_card_instance({"schema": "2.0"})


@pytest.mark.asyncio
async def test_create_card_instance_missing_id_raises(channel):
    channel._driver.cardkit_create = AsyncMock(return_value={"code": 0, "data": {}})
    with pytest.raises(FeishuChannelError):
        await channel.create_card_instance({"schema": "2.0"})


@pytest.mark.asyncio
async def test_send_card_by_reference_builds_interactive_message(channel):
    channel._sender.send = AsyncMock()
    await channel.send_card_by_reference("oc_chat_1", "card_abc")
    call = channel._sender.send.await_args
    sent = call.args[0]
    # OutboundCard with the reference-shape card payload
    assert sent.card == {"type": "card", "data": {"card_id": "card_abc"}}
    assert call.kwargs["receive_id"] == "oc_chat_1"
    assert call.kwargs["receive_id_type"] == "chat_id"


@pytest.mark.asyncio
async def test_send_card_by_reference_explicit_receive_type(channel):
    channel._sender.send = AsyncMock()
    await channel.send_card_by_reference(
        "user@example.com", "card_abc", receive_id_type="email"
    )
    assert channel._sender.send.await_args.kwargs["receive_id_type"] == "email"


@pytest.mark.asyncio
async def test_update_card_element_content_passes_sequence(channel):
    channel._driver.cardkit_update_element = AsyncMock(return_value={"code": 0})
    await channel.update_card_element_content(
        "card_abc", "el_1", "hello world", 7
    )
    call = channel._driver.cardkit_update_element.await_args
    assert call.kwargs["card_id"] == "card_abc"
    assert call.kwargs["element_id"] == "el_1"
    assert call.kwargs["body"] == {"content": "hello world", "sequence": 7}


@pytest.mark.asyncio
async def test_update_card_element_content_failure_raises(channel):
    channel._driver.cardkit_update_element = AsyncMock(
        return_value={"code": 400, "msg": "sequence out-of-order"}
    )
    with pytest.raises(FeishuChannelError):
        await channel.update_card_element_content("card_abc", "el_1", "...", 2)


@pytest.mark.asyncio
async def test_finish_streaming_card_posts_streaming_false(channel):
    channel._driver.cardkit_update_settings = AsyncMock(return_value={"code": 0})
    await channel.finish_streaming_card("card_abc", 99)
    call = channel._driver.cardkit_update_settings.await_args
    assert call.kwargs["card_id"] == "card_abc"
    body = call.kwargs["body"]
    assert body["sequence"] == 99
    parsed = json.loads(body["settings"])
    assert parsed == {"config": {"streaming_mode": False}}


@pytest.mark.asyncio
async def test_finish_streaming_card_failure_raises(channel):
    channel._driver.cardkit_update_settings = AsyncMock(
        return_value={"code": 400, "msg": "sequence out-of-order"}
    )
    with pytest.raises(FeishuChannelError):
        await channel.finish_streaming_card("card_abc", 1)
