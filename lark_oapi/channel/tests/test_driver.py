"""Driver smoke tests: verify the adapter correctly constructs SDK requests.

We don't hit the network — instead we patch the underlying Lark `Client`
service methods to record the built Request objects, then assert the
builders wired up fields as expected.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from lark_oapi.channel.driver import LarkClientDriver


def _stub_client():
    c = MagicMock()
    # im.v1.message.*
    msg = c.im.v1.message
    msg.acreate = AsyncMock(return_value=MagicMock(code=0, msg="", data=MagicMock(message_id="om_1")))
    msg.areply = AsyncMock(return_value=MagicMock(code=0, msg="", data=MagicMock(message_id="om_r")))
    msg.aupdate = AsyncMock(return_value=MagicMock(code=0, msg="", data=None))
    msg.apatch = AsyncMock(return_value=MagicMock(code=0, msg="", data=None))
    msg.adelete = AsyncMock(return_value=MagicMock(code=0, msg="", data=None))
    msg.aforward = AsyncMock(return_value=MagicMock(code=0, msg="", data=None))
    msg.aget = AsyncMock(return_value=MagicMock(code=0, msg="", data=MagicMock()))
    # im.v1.message_reaction.*
    rx = c.im.v1.message_reaction
    rx.acreate = AsyncMock(return_value=MagicMock(code=0, msg="", data=None))
    rx.adelete = AsyncMock(return_value=MagicMock(code=0, msg="", data=None))
    return c


@pytest.mark.asyncio
async def test_create_message_builds_request():
    c = _stub_client()
    d = LarkClientDriver(c)
    await d.create_message(
        receive_id_type="chat_id",
        receive_id="oc_1",
        msg_type="text",
        content='{"text": "hi"}',
        uuid="u1",
    )
    call = c.im.v1.message.acreate.call_args
    req = call.args[0]
    assert req.receive_id_type == "chat_id"
    assert req.body.receive_id == "oc_1"
    assert req.body.msg_type == "text"
    assert req.body.content == '{"text": "hi"}'
    assert req.body.uuid == "u1"


@pytest.mark.asyncio
async def test_reply_message_sets_thread_flag():
    c = _stub_client()
    d = LarkClientDriver(c)
    await d.reply_message(
        message_id="om_x",
        msg_type="text",
        content='{"text":"t"}',
        reply_in_thread=True,
    )
    call = c.im.v1.message.areply.call_args
    req = call.args[0]
    assert req.message_id == "om_x"
    assert req.body.reply_in_thread is True


@pytest.mark.asyncio
async def test_delete_forward_patch_use_correct_path():
    c = _stub_client()
    d = LarkClientDriver(c)
    await d.delete_message(message_id="om_del")
    assert c.im.v1.message.adelete.await_count == 1
    await d.patch_message(message_id="om_p", content="{}")
    assert c.im.v1.message.apatch.await_count == 1
    await d.forward_message(message_id="om_f", chat_id="oc_new")
    assert c.im.v1.message.aforward.await_count == 1
    fwd_call = c.im.v1.message.aforward.call_args
    assert fwd_call.args[0].receive_id_type == "chat_id"
    assert fwd_call.args[0].body.receive_id == "oc_new"


@pytest.mark.asyncio
async def test_update_message_sets_msg_type_and_content():
    c = _stub_client()
    d = LarkClientDriver(c)
    await d.update_message(
        message_id="om_update",
        msg_type="post",
        content='{"zh_cn":{"title":"","content":[]}}',
    )
    call = c.im.v1.message.aupdate.call_args
    req = call.args[0]
    assert req.message_id == "om_update"
    assert req.body.msg_type == "post"
    assert req.body.content == '{"zh_cn":{"title":"","content":[]}}'


@pytest.mark.asyncio
async def test_reaction_add_and_remove_call_correct_service():
    c = _stub_client()
    d = LarkClientDriver(c)
    await d.add_reaction(message_id="om_1", emoji_type="THUMBSUP")
    assert c.im.v1.message_reaction.acreate.await_count == 1
    await d.remove_reaction(message_id="om_1", reaction_id="rxn_1")
    assert c.im.v1.message_reaction.adelete.await_count == 1
