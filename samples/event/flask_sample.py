from flask import Flask

import lark_oapi as lark
from lark_oapi.adapter.flask import *
from lark_oapi.api.im.v1 import *

app = Flask(__name__)


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    print(lark.JSON.marshal(data))


def do_customized_event(data: lark.CustomizedEvent) -> None:
    print(lark.JSON.marshal(data))


handler = lark.EventDispatcherHandler.builder(lark.ENCRYPT_KEY, lark.VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("这里填入你要自定义订阅的 event 的 key,例如 out_approval", do_customized_event) \
    .build()


@app.route("/event", methods=["POST"])
def event():
    resp = handler.do(parse_req())
    return parse_resp(resp)


if __name__ == "__main__":
    app.run(port=7777)
