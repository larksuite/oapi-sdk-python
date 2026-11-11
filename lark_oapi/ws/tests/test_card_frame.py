import base64
import json
from unittest.mock import AsyncMock, Mock

import pytest

from lark_oapi.event.callback.model.p2_card_action_trigger import P2CardActionTriggerResponse
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws.client import Client
from lark_oapi.ws.const import HEADER_MESSAGE_ID, HEADER_SEQ, HEADER_SUM, HEADER_TRACE_ID, HEADER_TYPE
from lark_oapi.ws.enum import FrameType, MessageType
from lark_oapi.ws.pb.pbbp2_pb2 import Frame


@pytest.mark.parametrize("message_type", [MessageType.EVENT, MessageType.CARD])
async def test_card_callback_dispatch_and_reply(monkeypatch, message_type):
    callback = Mock(return_value=P2CardActionTriggerResponse({
        "toast": {"type": "success", "content": "Received"},
    }))
    dispatcher = (
        EventDispatcherHandler.builder("", "")
        .register_p2_card_action_trigger(callback)
        .build()
    )
    client = Client("test-app", "test-secret", event_handler=dispatcher)
    write_message = AsyncMock()
    monkeypatch.setattr(client, "_write_message", write_message)

    frame = Frame(SeqID=0, LogID=0, service=1, method=FrameType.DATA.value)
    for key, value in {
        HEADER_MESSAGE_ID: "test-message",
        HEADER_TRACE_ID: "test-trace",
        HEADER_SUM: "1",
        HEADER_SEQ: "0",
        HEADER_TYPE: message_type.value,
    }.items():
        frame.headers.add(key=key, value=value)
    frame.payload = json.dumps({
        "schema": "2.0",
        "header": {"event_type": "card.action.trigger"},
        "event": {"action": {"value": {"choice": "yes"}}},
    }).encode()

    await client._handle_message(frame.SerializeToString())

    callback.assert_called_once()
    assert callback.call_args.args[0].event.action.value == {"choice": "yes"}
    write_message.assert_awaited_once()
    reply = Frame()
    reply.ParseFromString(write_message.await_args.args[0])
    response = json.loads(reply.payload)
    assert response["code"] == 200
    assert json.loads(base64.b64decode(response["data"]))["toast"] == {
        "type": "success",
        "content": "Received",
    }
