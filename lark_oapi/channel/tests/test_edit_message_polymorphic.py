"""Polymorphic edit_message materialization tests."""

import json
from unittest.mock import AsyncMock

import pytest

from lark_oapi.channel import FeishuChannel
from lark_oapi.channel.config import MarkdownConverter, OutboundConfig
from lark_oapi.channel.outbound.sender import OutboundSender
from lark_oapi.channel.types import (
    MediaSource,
    OutboundCard,
    OutboundImage,
    OutboundPost,
    OutboundText,
)


@pytest.mark.asyncio
async def test_materialize_for_edit_text_body():
    s = OutboundSender(driver=None)
    body = await s.materialize_for_edit(OutboundText(text="plain"))
    assert body["msg_type"] == "text"
    assert json.loads(body["content"]) == {"text": "plain"}


@pytest.mark.asyncio
async def test_materialize_for_edit_markdown_native_body():
    cfg = OutboundConfig(markdown_converter=MarkdownConverter(tag_md_mode="native"))
    s = OutboundSender(driver=None, config=cfg)
    body = await s.materialize_for_edit(OutboundPost(markdown="# H1"))
    assert body["msg_type"] == "post"
    content = json.loads(body["content"])
    assert content["zh_cn"]["content"] == [[{"tag": "md", "text": "# H1"}]]


@pytest.mark.asyncio
async def test_materialize_for_edit_post_ast_opaque():
    ast = {"zh_cn": {"title": "", "content": [[{"tag": "text", "text": "hi"}]]}}
    s = OutboundSender(driver=None)
    body = await s.materialize_for_edit(OutboundPost(post=ast))
    assert body["msg_type"] == "post"
    assert json.loads(body["content"]) == ast


@pytest.fixture
def channel():
    ch = FeishuChannel(
        app_id="cli_x",
        app_secret="secret",
        outbound=OutboundConfig(markdown_converter=MarkdownConverter(tag_md_mode="native")),
    )
    ch._driver.update_message = AsyncMock(return_value={"code": 0, "data": {"message_id": "om_1"}})
    return ch


@pytest.mark.asyncio
async def test_edit_message_bare_string_aligns_with_send_as_markdown(channel):
    result = await channel.edit_message("om_1", "# H1")
    assert result.success is True
    channel._driver.update_message.assert_awaited_once()
    kwargs = channel._driver.update_message.await_args.kwargs
    assert kwargs["message_id"] == "om_1"
    assert kwargs["msg_type"] == "post"
    content = json.loads(kwargs["content"])
    assert content["zh_cn"]["content"] == [[{"tag": "md", "text": "# H1"}]]


@pytest.mark.asyncio
async def test_edit_message_text_dict_stays_text(channel):
    await channel.edit_message("om_1", {"text": "# literal"})
    kwargs = channel._driver.update_message.await_args.kwargs
    assert kwargs["msg_type"] == "text"
    assert json.loads(kwargs["content"]) == {"text": "# literal"}


@pytest.mark.asyncio
async def test_edit_message_markdown_dict_is_post(channel):
    await channel.edit_message("om_1", {"markdown": "**bold**"})
    kwargs = channel._driver.update_message.await_args.kwargs
    assert kwargs["msg_type"] == "post"
    content = json.loads(kwargs["content"])
    assert content["zh_cn"]["content"] == [[{"tag": "md", "text": "**bold**"}]]


@pytest.mark.asyncio
async def test_edit_message_post_dict_is_opaque(channel):
    ast = {"zh_cn": {"title": "", "content": [[{"tag": "text", "text": "opaque"}]]}}
    await channel.edit_message("om_1", {"post": ast})
    kwargs = channel._driver.update_message.await_args.kwargs
    assert kwargs["msg_type"] == "post"
    assert json.loads(kwargs["content"]) == ast


@pytest.mark.asyncio
async def test_edit_message_rejects_card_and_mentions_update_card(channel):
    with pytest.raises(TypeError, match="update_card"):
        await channel.edit_message("om_1", OutboundCard(card={"schema": "2.0"}))
    channel._driver.update_message.assert_not_called()


@pytest.mark.asyncio
async def test_edit_message_rejects_media(channel):
    with pytest.raises(TypeError, match="text/post"):
        await channel.edit_message(
            "om_1",
            OutboundImage(source=MediaSource(kind="key", key="img_x")),
        )
    channel._driver.update_message.assert_not_called()
