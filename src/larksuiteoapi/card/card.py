# -*- coding: UTF-8 -*-


from typing import Any, Callable, Union, Dict

from ..config import Config
from ..context import Context
from ..model.oapi_request import OapiRequest
from ..model.oapi_response import OapiResponse
from .handler.handlers import CardHandlers
from .handler.manager import Manager
from .model.card import HTTPCard, Card


def set_card_callback(conf, callback):
    # type: (Config, Callable[[Context, Config, Card], Union[None, Dict]]) -> None
    Manager.set_callback(conf, callback)


def handle_card(conf, req):
    # type: (Config, OapiRequest) -> OapiResponse
    http_card = HTTPCard()
    http_card.request = req
    http_card.response = OapiResponse()
    CardHandlers(conf, http_card).handler()
    return http_card.response
