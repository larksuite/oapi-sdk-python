from flask import Flask

import lark_oapi as lark
from event.callback.model.p2_card_action_trigger import P2CardActionTrigger, P2CardActionTriggerResponse
from event.callback.model.p2_url_preview_get import P2URLPreviewGet, P2URLPreviewGetResponse
from lark_oapi.adapter.flask import *
from lark_oapi.api.im.v1 import *

app = Flask(__name__)


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    print(lark.JSON.marshal(data))


def do_customized_event(data: lark.CustomizedEvent) -> None:
    print(lark.JSON.marshal(data))


# 新版卡片回调，卡片回传交互 card.action.trigger
def do_card_action_trigger(data: P2CardActionTrigger) -> P2CardActionTriggerResponse:
    print(lark.JSON.marshal(data))
    resp = {
        "toast": {
            "type": "info",
            "content": "卡片回传成功 from python sdk"
        }
    }
    return P2CardActionTriggerResponse(resp)


def do_url_preview_get(data: P2URLPreviewGet) -> P2URLPreviewGetResponse:
    print(lark.JSON.marshal(data))
    resp = {
        "inline": {
            "title": "链接预览测试",
        }
    }
    return P2URLPreviewGetResponse(resp)


handler = lark.EventDispatcherHandler.builder(lark.ENCRYPT_KEY, lark.VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_card_action_trigger(do_card_action_trigger) \
    .register_p2_url_preview_get(do_url_preview_get) \
    .register_p1_customized_event("这里填入你要自定义订阅的 event 的 key,例如 out_approval", do_customized_event) \
    .build()


@app.route("/event", methods=["POST"])
def event():
    resp = handler.do(parse_req())
    return parse_resp(resp)


if __name__ == "__main__":
    app.run(port=7777)
