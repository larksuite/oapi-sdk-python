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
from ..model.get_chat_announcement_request import GetChatAnnouncementRequest
from ..model.get_chat_announcement_response import GetChatAnnouncementResponse
from ..model.patch_chat_announcement_request import PatchChatAnnouncementRequest
from ..model.patch_chat_announcement_response import PatchChatAnnouncementResponse


class ChatAnnouncement(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def get(self, request: GetChatAnnouncementRequest,
            option: Optional[RequestOption] = None) -> GetChatAnnouncementResponse:
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
        response: GetChatAnnouncementResponse = JSON.unmarshal(str(resp.content, UTF_8), GetChatAnnouncementResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetChatAnnouncementRequest,
                   option: Optional[RequestOption] = None) -> GetChatAnnouncementResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetChatAnnouncementResponse = JSON.unmarshal(str(resp.content, UTF_8), GetChatAnnouncementResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchChatAnnouncementRequest,
              option: Optional[RequestOption] = None) -> PatchChatAnnouncementResponse:
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
        response: PatchChatAnnouncementResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                 PatchChatAnnouncementResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchChatAnnouncementRequest,
                     option: Optional[RequestOption] = None) -> PatchChatAnnouncementResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchChatAnnouncementResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                 PatchChatAnnouncementResponse)
        response.raw = resp

        return response
