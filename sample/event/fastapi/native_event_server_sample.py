# -*- coding: UTF-8 -*-

import uvicorn

from larksuiteoapi.event import handle_event, set_event_callback
from larksuiteoapi.model import OapiHeader, OapiRequest

from fastapi import FastAPI, Request, Response

from larksuiteoapi import Config, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# for memory store and logger(level=debug)
conf = Config(DOMAIN_FEISHU, app_settings, log_level=LEVEL_DEBUG)

app = FastAPI()


def app_open_event_handle(ctx, conf, event):
    # type: (Context, Config, dict) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event)


# set event type 'app_status_change' handle
set_event_callback(conf, 'app_open', app_open_event_handle)


@app.post('/webhook/event')
async def webhook_event(request: Request, resp: Response):
    oapi_request = OapiRequest(uri=request.url.path, body=await request.body(), header=OapiHeader(request.headers))
    oapi_resp = handle_event(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.body = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


# 设置 "开发者后台" -> "事件订阅" 请求网址 URL：https://domain/webhook/event
# startup event http server, port: 8000
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
