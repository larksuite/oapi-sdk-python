# -*- coding: UTF-8 -*-
from typing import Any, Union, Dict

from larksuiteoapi.config import Config
from larksuiteoapi.model.oapi_header import OapiHeader
from larksuiteoapi.model.oapi_request import OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi.card import Card, set_card_callback, handle_card

from sample.config.config import test_config_with_memory_store, test_config_with_redis_store
from larksuiteoapi import Context, DOMAIN_FEISHU, DOMAIN_LARK_SUITE

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for redis store and logger(level=debug)
conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)


# for memory store and logger(level=debug)
# conf = test_config_with_memory_store(DOMAIN_FEISHU, app_settings)


def handle(ctx, conf, card):
    # type: (Context, Config, Card) -> Union[None, Dict]
    print(ctx.get_header().items())
    print('card = %s' % card)
    return {
        "config": {
            "wide_screen_mode": True
        },
        "card_link": {
            "url": "https://www.baidu.com",
            "android_url": "https://developer.android.com/",
            "ios_url": "https://developer.apple.com/",
            "pc_url": "https://www.windows.com"
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "this is header"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "This is a very very very very very very very long text;"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "Read"
                        },
                        "type": "default"
                    }
                ]
            }
        ]
    }


set_card_callback(conf, handle)
app = Flask(__name__)


@app.route('/webhook/card', methods=['GET', 'POST'])
def webhook_card():
    oapi_request = OapiRequest(uri=request.path, body=request.data, header=OapiHeader(request.headers))
    resp = make_response()
    oapi_resp = handle_card(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.data = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")
