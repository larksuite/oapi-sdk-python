# -*- coding: UTF-8 -*-

from typing import Any, Callable

from ..config import Config
from ..context import Context
from ..model.oapi_request import OapiRequest
from ..model.oapi_response import OapiResponse
from .app.ticket import set_app_ticket_event_handler
from .handler.handlers import EventHandlers
from .handler.manager import Manager
from .model.event import HTTPEvent


def set_event_callback(conf, event_type, callback, clazz=dict):
    # type: (Config, str, Callable[[Context, Config, Any], Any], Any) -> None

    Manager.set_event_callback(conf, event_type, callback, clazz=clazz)


def handle_event(conf, req):
    # type: (Config, OapiRequest) -> OapiResponse
    http_event = HTTPEvent(request=req)

    if Manager.get_event_callback(conf, 'app_ticket') is None:
        set_app_ticket_event_handler(conf)
    EventHandlers(conf, http_event).handle()
    return http_event.response
