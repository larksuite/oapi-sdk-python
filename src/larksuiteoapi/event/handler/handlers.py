# -*- coding: UTF-8 -*-

import json
from typing import Union

from ...config import Config
from ...consts import *
from ...context import Context
from ...model import OapiResponse
from ...utils import make_datatype, decrypt
from ..handler.manager import Manager
from ..model.error import HandlerNotFoundError
from ..model.event import Fuzzy, HTTPEvent

VERSION_1 = "1.0"
VERSION_2 = "2.0"
RESPONSE_FORMAT = '{"codemsg":"%s"}'
CHALLENGE_RESPONSE_FORMAT = '{"challenge":"%s"}'
CALLBACK_TYPE_EVENT = "event_callback"
CALLBACK_TYPE_CHALLENGE = "url_verification"

HTTP_STATUS_OK = 200
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500


class EventHandlers(object):

    def __init__(self, conf, httpEvent):
        # type: (Config, HTTPEvent) -> None
        self.httpEvent = httpEvent
        self.conf = conf
        self.ctx = Context()

    def parse(self):  # type: () -> None
        httpEvent, conf, ctx = self.httpEvent, self.conf, self.ctx
        req = httpEvent.request
        ctx.set(HTTP_HEADER_KEY, req.header)
        encrypt_key = conf.app_settings.encrypt_key
        if encrypt_key is not None and encrypt_key != "":
            req.body = decrypt(req.body, conf.app_settings.encrypt_key.encode("utf-8"))
        eventDict = json.loads(req.body)

        fuzzy = make_datatype(Fuzzy, eventDict)
        schema = VERSION_1
        if fuzzy.schema:
            schema = fuzzy.schema
        token = fuzzy.token
        event_type = CALLBACK_TYPE_CHALLENGE
        if fuzzy.event:
            event_type = fuzzy.event.type
        if fuzzy.header:
            token, event_type = fuzzy.header.token, fuzzy.header.event_type
        httpEvent.schema = schema
        httpEvent.event_type = event_type
        httpEvent.type = fuzzy.type
        httpEvent.challenge = fuzzy.challenge

        if token != conf.app_settings.verification_token:
            raise RuntimeError('New token invalid, received=%s, configured=%s' % (
                token, conf.app_settings.verification_token))

        data_type = Manager.get_event_type(conf, httpEvent.event_type)
        httpEvent.data = make_datatype(data_type, eventDict)

    def handler(self):  # type: () -> None
        ctx, conf, event = self.ctx, self.conf, self.httpEvent
        if event.type == CALLBACK_TYPE_CHALLENGE:
            return

        h = Manager.get_event_callback(conf, event.event_type)
        if h is None:
            raise HandlerNotFoundError(
                'event-type:%s, handler not found' % event.event_type)

        event.ctx = ctx
        h(ctx, conf, event.data)

    def complement(self, exception):  # type: (Union[None, Exception]) -> None
        conf, event = self.conf, self.httpEvent
        if exception:
            if isinstance(exception, HandlerNotFoundError):
                body = RESPONSE_FORMAT % exception.__str__()
                self.write_response(
                    HTTP_STATUS_OK, DEFAULT_CONTENT_TYPE, body.encode('utf-8'))
            else:
                err_msg = 'err occurred, %s' % exception.__str__()
                body = RESPONSE_FORMAT % exception.__str__()
                self.write_response(HTTP_STATUS_INTERNAL_SERVER_ERROR, DEFAULT_CONTENT_TYPE,
                                    body.encode('utf-8'))
                conf.logger.error(err_msg)
            return

        if event.type == CALLBACK_TYPE_CHALLENGE:
            self.write_response(HTTP_STATUS_OK, DEFAULT_CONTENT_TYPE,
                                (CHALLENGE_RESPONSE_FORMAT % event.challenge).encode('utf-8'))
            return

        self.write_response(HTTP_STATUS_OK, DEFAULT_CONTENT_TYPE,
                            (RESPONSE_FORMAT % 'success').encode('utf-8'))

    def write_response(self, status_code, content_type, body):
        # type: (int, str, Union[str, bytes]) -> None
        resp = OapiResponse()

        if isinstance(body, str):
            body = body.encode('utf-8')
        resp.status_code = status_code
        resp.content_type = content_type
        resp.body = body
        self.httpEvent.response = resp

    def handle(self):  # type: () -> None
        exception = None  # type: Union[None, Exception]
        try:
            self.parse()
            self.handler()
        except Exception as e:
            exception = e
        finally:
            self.complement(exception)
