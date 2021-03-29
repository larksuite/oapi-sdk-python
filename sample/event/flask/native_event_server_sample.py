# -*- coding: UTF-8 -*-

from larksuiteoapi.event import handle_event
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, DOMAIN_FEISHU

# 应用商店应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_isv_app_settings_from_env("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_isv_app_settings_from_env()

# 当前访问的是飞书，使用redis store，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config(DOMAIN_FEISHU, app_settings, app_settings, logger, log_level, store)

app = Flask(__name__)


@app.route('/webhook/event', methods=['POST'])
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
