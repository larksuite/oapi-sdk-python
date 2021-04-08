# -*- coding: UTF-8 -*-
import json
from hashlib import sha1
from typing import Any, Union

from ...utils import make_datatype
from ...config import Config
from ...consts import *
from ...context import Context
from ..model.card import Challenge, Header, HTTPCard, Card
from ..model.error import *
from .manager import Manager

LARK_REQUEST_TIMESTAMP = "X-Lark-Request-Timestamp"
LARK_REQUEST_REQUEST_NONCE = "X-Lark-Request-Nonce"
LARK_SIGNATURE = "X-Lark-Signature"
LARK_REFRESH_TOKEN = "X-Refresh-Token"
CALLBACK_TYPE_CHALLENGE = "url_verification"
RESPONSE_FORMAT = '{"codemsg":"%s"}'
CHALLENGE_RESPONSE_FORMAT = '{"challenge":"%s"}'

HTTP_STATUS_OK = 200
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500


class CardHandlers(object):

    def __init__(self, conf, httpCard):
        # type: (Config, HTTPCard) -> None
        self.conf = conf
        self.header = Header()
        self.httpCard = httpCard
        self.respBody = None  # type: Union[None, Any]
        self.ctx = Context()

    def init(self):  # type: () -> None
        req, ctx = self.httpCard.request, self.ctx
        __headers = req.header
        ctx.set(HTTP_HEADER_KEY, __headers)
        time_stamp = __headers.first_value(LARK_REQUEST_TIMESTAMP)
        nonce = __headers.first_value(LARK_REQUEST_REQUEST_NONCE)
        signature = __headers.first_value(LARK_SIGNATURE)
        refresh_token = __headers.first_value(LARK_REFRESH_TOKEN)
        self.header.time_stamp = time_stamp
        self.header.nonce = nonce
        self.header.signature = signature
        self.header.refresh_token = refresh_token

    def validate(self):  # type: () -> None
        httpCard, conf = self.httpCard, self.conf
        if not self.header.signature:
            return
        settings = conf.app_settings
        body = httpCard.request.body.decode('utf-8')
        signature = CardHandlers.__signature(self.header.nonce, self.header.time_stamp, body,
                                             settings.verification_token)
        if self.header.signature != signature:
            raise SignatureError('signature error')

    @staticmethod
    def __signature(nonce, timestamp, body, token):  # type: (str, str, str, str) -> str
        buf = '%s%s%s%s' % (timestamp, nonce, token, body)
        sha1_obj = sha1()
        sha1_obj.update(buf.encode('utf-8'))
        return sha1_obj.hexdigest()

    def parse(self):  # type: () -> None
        httpCard, conf = self.httpCard, self.conf
        req = httpCard.request
        req.body = json.loads(req.body)
        challenge = make_datatype(Challenge, req.body)
        httpCard.type = challenge.type
        httpCard.challenge = challenge.challenge
        if httpCard.type == CALLBACK_TYPE_CHALLENGE \
                and conf.app_settings.verification_token != challenge.token:
            raise TokenInvalidError(
                'AppSettings.verificationToken not equal token(%s)' % challenge.token)

    def handle(self):  # type: () -> None
        ctx, conf, httpCard = self.ctx, self.conf, self.httpCard
        if httpCard.type == CALLBACK_TYPE_CHALLENGE:
            return

        h = Manager.get_callback(conf)
        if h is None:
            raise HandlerNotFoundError('handler not found')
        card = make_datatype(Card, self.httpCard.request.body)
        self.respBody = h(ctx, conf, card)

    def complement(self, exception):  # type: (Union[None, Exception]) -> None
        card, conf = self.httpCard, self.conf

        if exception is not None:
            if isinstance(exception, HandlerNotFoundError):
                status_code = HTTP_STATUS_INTERNAL_SERVER_ERROR
                content_type = DEFAULT_CONTENT_TYPE
                body = RESPONSE_FORMAT % exception.__str__()
                err_msg = 'handler not found, %s' % exception.__str__()
            else:
                status_code = HTTP_STATUS_INTERNAL_SERVER_ERROR
                content_type = DEFAULT_CONTENT_TYPE
                body = RESPONSE_FORMAT % exception.__str__()
                err_msg = 'err occurred, %s' % exception.__str__()

            self.write_response(status_code, content_type, body)
            conf.logger.error('request_id=%s err_msg=%s' % (self.ctx.get_request_id(), err_msg))
            return

        if card.type == CALLBACK_TYPE_CHALLENGE:
            self.write_response(
                HTTP_STATUS_OK, DEFAULT_CONTENT_TYPE,
                CHALLENGE_RESPONSE_FORMAT % card.challenge)
            return

        if self.respBody is not None:
            if isinstance(self.respBody, dict):
                body = json.dumps(self.respBody)
            else:
                body = self.respBody
            self.write_response(HTTP_STATUS_OK, DEFAULT_CONTENT_TYPE, body)
        else:
            self.write_response(HTTP_STATUS_OK, DEFAULT_CONTENT_TYPE, RESPONSE_FORMAT % 'success')

    def handler(self):  # type: () -> None
        try:
            self.init()
            self.validate()
            self.parse()
            self.handle()
        except Exception as e:
            self.complement(e)
        else:
            self.complement(None)

    def write_response(self, status_code, content_type, body):
        # type: (int, str, Union[str, bytes]) -> None
        resp = self.httpCard.response
        if isinstance(body, str):
            body = body.encode('utf-8')
        resp.status_code = status_code
        resp.content_type = content_type
        resp.body = body
