# -*- coding: UTF-8 -*-
import attr

from larksuiteoapi.event import handle_event, set_event_callback
from larksuiteoapi.event.model import BaseEvent
from larksuiteoapi.model import OapiHeader, OapiRequest
from larksuiteoapi.service.contact.v3 import UserUpdatedEventHandler, UserUpdatedEvent

from flask import Flask, request
from flask.helpers import make_response

from sample.config.config import test_config_with_memory_store, test_config_with_redis_store
from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DOMAIN_LARK_SUITE

# for Cutome APP（企业自建应用）

app_settings = Config.new_internal_app_settings_from_env()

# for redis store and logger(level=debug)
conf = test_config_with_redis_store(DOMAIN_FEISHU, app_settings)


# for memory store and logger(level=debug)
# conf = test_config_with_memory_store(DOMAIN_FEISHU, app_settings)


@attr.s
class ApplicationAppStatusChangeEventData(object):
    app_id = attr.ib(type=str, default='')
    tenant_key = attr.ib(type=str, default='')
    type = attr.ib(type=str, default='')
    status = attr.ib(type=str, default='')


@attr.s
class ApplicationAppStatusChangeEvent(BaseEvent):
    event = attr.ib(type=ApplicationAppStatusChangeEventData, default=None)


def app_status_change_event_handler(ctx, conf, event):
    # type: (Context, Config, ApplicationAppStatusChangeEvent) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event.event.type)


def user_change(ctx, conf, event):
    # type: (Context, Config, dict) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event)


set_event_callback(conf, 'app_status_change', app_status_change_event_handler, ApplicationAppStatusChangeEvent)

set_event_callback(conf, 'user_update', user_change)


def user_update(ctx, conf, event):
    # type: (Context, Config, UserUpdatedEvent) ->None
    print(ctx.get_request_id())
    print(event.header)
    print(event.event)
    pass


UserUpdatedEventHandler.set_callback(conf, user_update)

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


if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")
