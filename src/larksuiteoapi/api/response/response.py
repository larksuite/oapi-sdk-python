# -*- coding: UTF-8 -*-

from typing import Union, TypeVar, Generic, List

from ...model import OapiHeader
from ...context import Context
from ...consts import ERR_CODE_OK
import attr

T = TypeVar('T')


@attr.s
class ErrorDetail(object):
    key = attr.ib(type=str, default='')
    value = attr.ib(type=str, default='')


@attr.s
class PermissionViolation(object):
    key = attr.ib(type=str, default='')
    subject = attr.ib(type=str, default='')
    description = attr.ib(type=str, default='')


@attr.s
class FieldViolation(object):
    field = attr.ib(type=str, default='')
    value = attr.ib(type=str, default='')
    description = attr.ib(type=str, default='')


@attr.s
class ErrorHelp(object):
    url = attr.ib(type=str, default='')
    description = attr.ib(type=str, default='')


@attr.s
class ResponseError(object):
    details = attr.ib(type=List[ErrorDetail], default=None)
    permission_violations = attr.ib(type=List[PermissionViolation], default=None)
    field_violations = attr.ib(type=List[FieldViolation], default=None)
    helps = attr.ib(type=List[ErrorHelp], default=None)


class Response(Generic[T]):

    def __init__(self, ctx, code=ERR_CODE_OK, data=None, msg='', error=None):
        # type: (Context, int, T,  str, ResponseError) -> None
        self.ctx = ctx
        self.code = code
        self.data = data
        self.error = error
        self.msg = msg

    def get_header(self):  # type: () -> OapiHeader
        return self.ctx.get_header()

    def get_request_id(self):  # type: () -> Union[None, str]
        return self.ctx.get_request_id()

    def get_http_status_code(self):  # type: () -> Union[None, int]
        return self.ctx.get_http_status_code()

    def __str__(self):
        return 'response, request_id:%s, status_code:%d, code:%d, msg:%s, data: %s' % (self.get_request_id(),
                                                                                       self.get_http_status_code(),
                                                                                       self.code, self.msg, self.data)