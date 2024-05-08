from typing import Any

from flask import Flask

import lark_oapi as lark
from lark_oapi.adapter.flask import *

app = Flask(__name__)


def do_interactive_card(data: lark.Card) -> Any:
    print(lark.JSON.marshal(data))
    content = {
        "toast":{
            "type":"info",
            "content":"卡片交互成功",
            "i18n":{
                "zh_cn":"卡片交互成功",
                "en_us":"card action success"
            }
        },
        "card":{
            "type":"raw",
            "data":{
                "config":{
                    "enable_forward":True
                },
                "elements":[
                    {
                        "tag":"div",
                        "text":{
                            "content":"This is the plain text",
                            "tag":"plain_text"
                        }
                    }
                ],
                "header":{
                    "template":"blue",
                    "title":{
                        "content":"This is the title",
                        "tag":"plain_text"
                    }
                }
            }
        }
    }
    return content


handler = lark.CardActionHandler.builder(lark.ENCRYPT_KEY, lark.VERIFICATION_TOKEN, lark.LogLevel.DEBUG) \
    .register(do_interactive_card) \
    .build()


@app.route("/card", methods=["POST"])
def card():
    resp = handler.do(parse_req())
    return parse_resp(resp)


if __name__ == "__main__":
    app.run(port=7777)
