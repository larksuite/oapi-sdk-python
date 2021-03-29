# -*- coding: UTF-8 -*-

from larksuiteoapi.event import handle_event
from larksuiteoapi.service.contact.v3 import UserUpdatedEventHandler, UserUpdatedEvent
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


def user_update_handle(ctx, conf, event):
    # type: (Context, Config, UserUpdatedEvent) ->None
    print(ctx.get_request_id())
    print(event.header)
    print(event.event)
    pass


# set event type 'contact.user.updated_v3' handle
UserUpdatedEventHandler.set_callback(conf, user_update_handle)

app = Flask(__name__)


@app.route('/webhook/event', methods=['GET', 'POST'])
def webhook_event():
    oapi_request = OapiRequest(uri=request.path, body=request.data, header=OapiHeader(request.headers))
    resp = make_response()
    oapi_resp = handle_event(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.data = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


# 设置 "开发者后台" -> "事件订阅" 请求网址 URL：https://domain/webhook/event
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")
