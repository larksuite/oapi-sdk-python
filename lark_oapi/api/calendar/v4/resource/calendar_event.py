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
from ..model.create_calendar_event_request import CreateCalendarEventRequest
from ..model.create_calendar_event_response import CreateCalendarEventResponse
from ..model.delete_calendar_event_request import DeleteCalendarEventRequest
from ..model.delete_calendar_event_response import DeleteCalendarEventResponse
from ..model.get_calendar_event_request import GetCalendarEventRequest
from ..model.get_calendar_event_response import GetCalendarEventResponse
from ..model.instance_view_calendar_event_request import InstanceViewCalendarEventRequest
from ..model.instance_view_calendar_event_response import InstanceViewCalendarEventResponse
from ..model.instances_calendar_event_request import InstancesCalendarEventRequest
from ..model.instances_calendar_event_response import InstancesCalendarEventResponse
from ..model.list_calendar_event_request import ListCalendarEventRequest
from ..model.list_calendar_event_response import ListCalendarEventResponse
from ..model.patch_calendar_event_request import PatchCalendarEventRequest
from ..model.patch_calendar_event_response import PatchCalendarEventResponse
from ..model.reply_calendar_event_request import ReplyCalendarEventRequest
from ..model.reply_calendar_event_response import ReplyCalendarEventResponse
from ..model.search_calendar_event_request import SearchCalendarEventRequest
from ..model.search_calendar_event_response import SearchCalendarEventResponse
from ..model.subscription_calendar_event_request import SubscriptionCalendarEventRequest
from ..model.subscription_calendar_event_response import SubscriptionCalendarEventResponse
from ..model.unsubscription_calendar_event_request import UnsubscriptionCalendarEventRequest
from ..model.unsubscription_calendar_event_response import UnsubscriptionCalendarEventResponse


class CalendarEvent(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateCalendarEventRequest,
               option: Optional[RequestOption] = None) -> CreateCalendarEventResponse:
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
        response: CreateCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateCalendarEventResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateCalendarEventRequest,
                      option: Optional[RequestOption] = None) -> CreateCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateCalendarEventResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteCalendarEventRequest,
               option: Optional[RequestOption] = None) -> DeleteCalendarEventResponse:
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
        response: DeleteCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteCalendarEventResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteCalendarEventRequest,
                      option: Optional[RequestOption] = None) -> DeleteCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteCalendarEventResponse)
        response.raw = resp

        return response

    def get(self, request: GetCalendarEventRequest, option: Optional[RequestOption] = None) -> GetCalendarEventResponse:
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
        response: GetCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), GetCalendarEventResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetCalendarEventRequest,
                   option: Optional[RequestOption] = None) -> GetCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), GetCalendarEventResponse)
        response.raw = resp

        return response

    def instance_view(self, request: InstanceViewCalendarEventRequest,
                      option: Optional[RequestOption] = None) -> InstanceViewCalendarEventResponse:
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
        response: InstanceViewCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                     InstanceViewCalendarEventResponse)
        response.raw = resp

        return response

    async def ainstance_view(self, request: InstanceViewCalendarEventRequest,
                             option: Optional[RequestOption] = None) -> InstanceViewCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: InstanceViewCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                     InstanceViewCalendarEventResponse)
        response.raw = resp

        return response

    def instances(self, request: InstancesCalendarEventRequest,
                  option: Optional[RequestOption] = None) -> InstancesCalendarEventResponse:
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
        response: InstancesCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  InstancesCalendarEventResponse)
        response.raw = resp

        return response

    async def ainstances(self, request: InstancesCalendarEventRequest,
                         option: Optional[RequestOption] = None) -> InstancesCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: InstancesCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  InstancesCalendarEventResponse)
        response.raw = resp

        return response

    def list(self, request: ListCalendarEventRequest,
             option: Optional[RequestOption] = None) -> ListCalendarEventResponse:
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
        response: ListCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), ListCalendarEventResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListCalendarEventRequest,
                    option: Optional[RequestOption] = None) -> ListCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), ListCalendarEventResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchCalendarEventRequest,
              option: Optional[RequestOption] = None) -> PatchCalendarEventResponse:
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
        response: PatchCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchCalendarEventResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchCalendarEventRequest,
                     option: Optional[RequestOption] = None) -> PatchCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchCalendarEventResponse)
        response.raw = resp

        return response

    def reply(self, request: ReplyCalendarEventRequest,
              option: Optional[RequestOption] = None) -> ReplyCalendarEventResponse:
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
        response: ReplyCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), ReplyCalendarEventResponse)
        response.raw = resp

        return response

    async def areply(self, request: ReplyCalendarEventRequest,
                     option: Optional[RequestOption] = None) -> ReplyCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ReplyCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), ReplyCalendarEventResponse)
        response.raw = resp

        return response

    def search(self, request: SearchCalendarEventRequest,
               option: Optional[RequestOption] = None) -> SearchCalendarEventResponse:
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
        response: SearchCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), SearchCalendarEventResponse)
        response.raw = resp

        return response

    async def asearch(self, request: SearchCalendarEventRequest,
                      option: Optional[RequestOption] = None) -> SearchCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: SearchCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8), SearchCalendarEventResponse)
        response.raw = resp

        return response

    def subscription(self, request: SubscriptionCalendarEventRequest,
                     option: Optional[RequestOption] = None) -> SubscriptionCalendarEventResponse:
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
        response: SubscriptionCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                     SubscriptionCalendarEventResponse)
        response.raw = resp

        return response

    async def asubscription(self, request: SubscriptionCalendarEventRequest,
                            option: Optional[RequestOption] = None) -> SubscriptionCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: SubscriptionCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                     SubscriptionCalendarEventResponse)
        response.raw = resp

        return response

    def unsubscription(self, request: UnsubscriptionCalendarEventRequest,
                       option: Optional[RequestOption] = None) -> UnsubscriptionCalendarEventResponse:
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
        response: UnsubscriptionCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                       UnsubscriptionCalendarEventResponse)
        response.raw = resp

        return response

    async def aunsubscription(self, request: UnsubscriptionCalendarEventRequest,
                              option: Optional[RequestOption] = None) -> UnsubscriptionCalendarEventResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: UnsubscriptionCalendarEventResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                       UnsubscriptionCalendarEventResponse)
        response.raw = resp

        return response
