from typing import Any

from flask import Flask

import lark_oapi as lark
from lark_oapi.adapter.flask import *

app = Flask(__name__)


def do_interactive_card(data: lark.Card) -> Any:
    print(lark.JSON.marshal(data))
    content = {
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "更新卡片成功"
            },
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**Success!\n成功啦😄**"
                }
            },
        ]
    }
    return content


handler = lark.CardActionHandler.builder(lark.ENCRYPT_KEY, lark.VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register(do_interactive_card) \
    .build()


@app.route("/card", methods=["POST"])
def event():
    resp = handler.do(parse_req())
    return parse_resp(resp)


if __name__ == "__main__":
    app.run(port=7777)
