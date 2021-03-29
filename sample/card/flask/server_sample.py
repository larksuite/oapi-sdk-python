# -*- coding: UTF-8 -*-
from typing import Any, Union, Dict

from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

from larksuiteoapi.card import Card, set_card_callback, handle_card

from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


# 设置消息卡片的处理
# 返回值：可以为None、新的消息卡片的Json（dict）
def handle(ctx, conf, card):
    # type: (Context, Config, Card) -> Union[None, Dict]
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


@app.route('/webhook/card', methods=['POST'])
def webhook_card():
    oapi_request = OapiRequest(uri=request.path, body=request.data, header=OapiHeader(request.headers))
    resp = make_response()
    oapi_resp = handle_card(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.data = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


# 设置 "开发者后台" -> "应用功能" -> "机器人" 消息卡片请求网址：https://domain/webhook/card
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")
