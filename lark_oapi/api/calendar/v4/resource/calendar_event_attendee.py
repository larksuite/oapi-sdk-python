# Code generated by Lark OpenAPI.

import io
from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.const import UTF_8, CONTENT_TYPE, APPLICATION_JSON
from lark_oapi.core import JSON
from lark_oapi.core.token import verify
from lark_oapi.core.http import Transport
from lark_oapi.core.model import Config, RequestOption, RawResponse
from lark_oapi.core.utils import Files
from requests_toolbelt import MultipartEncoder
from ..model.batch_delete_calendar_event_attendee_request import BatchDeleteCalendarEventAttendeeRequest
from ..model.batch_delete_calendar_event_attendee_response import BatchDeleteCalendarEventAttendeeResponse
from ..model.create_calendar_event_attendee_request import CreateCalendarEventAttendeeRequest
from ..model.create_calendar_event_attendee_response import CreateCalendarEventAttendeeResponse
from ..model.list_calendar_event_attendee_request import ListCalendarEventAttendeeRequest
from ..model.list_calendar_event_attendee_response import ListCalendarEventAttendeeResponse


class CalendarEventAttendee(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def batch_delete(self, request: BatchDeleteCalendarEventAttendeeRequest,
                     option: Optional[RequestOption] = None) -> BatchDeleteCalendarEventAttendeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 添加 content-type
        if request.body is not None:
            option.headers[CONTENT_TYPE] = f"{APPLICATION_JSON}; charset=utf-8"

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: BatchDeleteCalendarEventAttendeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            BatchDeleteCalendarEventAttendeeResponse)
        response.raw = resp

        return response

    async def abatch_delete(self, request: BatchDeleteCalendarEventAttendeeRequest,
                            option: Optional[RequestOption] = None) -> BatchDeleteCalendarEventAttendeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: BatchDeleteCalendarEventAttendeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            BatchDeleteCalendarEventAttendeeResponse)
        response.raw = resp

        return response

    def create(self, request: CreateCalendarEventAttendeeRequest,
               option: Optional[RequestOption] = None) -> CreateCalendarEventAttendeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 添加 content-type
        if request.body is not None:
            option.headers[CONTENT_TYPE] = f"{APPLICATION_JSON}; charset=utf-8"

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: CreateCalendarEventAttendeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                       CreateCalendarEventAttendeeResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateCalendarEventAttendeeRequest,
                      option: Optional[RequestOption] = None) -> CreateCalendarEventAttendeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateCalendarEventAttendeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                       CreateCalendarEventAttendeeResponse)
        response.raw = resp

        return response

    def list(self, request: ListCalendarEventAttendeeRequest,
             option: Optional[RequestOption] = None) -> ListCalendarEventAttendeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 添加 content-type
        if request.body is not None:
            option.headers[CONTENT_TYPE] = f"{APPLICATION_JSON}; charset=utf-8"

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: ListCalendarEventAttendeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                     ListCalendarEventAttendeeResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListCalendarEventAttendeeRequest,
                    option: Optional[RequestOption] = None) -> ListCalendarEventAttendeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListCalendarEventAttendeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                     ListCalendarEventAttendeeResponse)
        response.raw = resp

        return response
