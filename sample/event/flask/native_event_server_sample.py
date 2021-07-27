# -*- coding: UTF-8 -*-

from larksuiteoapi.event import handle_event, set_event_callback
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for memory store and logger(level=debug)
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)

app = Flask(__name__)


def app_open_event_handle(ctx, conf, event):
    # type: (Context, Config, dict) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event)


# set event type 'app_status_change' handle
set_event_callback(conf, 'app_open', app_open_event_handle)


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
