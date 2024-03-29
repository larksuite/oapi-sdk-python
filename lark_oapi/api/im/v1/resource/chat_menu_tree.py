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
from ..model.create_chat_menu_tree_request import CreateChatMenuTreeRequest
from ..model.create_chat_menu_tree_response import CreateChatMenuTreeResponse
from ..model.delete_chat_menu_tree_request import DeleteChatMenuTreeRequest
from ..model.delete_chat_menu_tree_response import DeleteChatMenuTreeResponse
from ..model.get_chat_menu_tree_request import GetChatMenuTreeRequest
from ..model.get_chat_menu_tree_response import GetChatMenuTreeResponse
from ..model.sort_chat_menu_tree_request import SortChatMenuTreeRequest
from ..model.sort_chat_menu_tree_response import SortChatMenuTreeResponse


class ChatMenuTree(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateChatMenuTreeRequest,
               option: Optional[RequestOption] = None) -> CreateChatMenuTreeResponse:
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
        response: CreateChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateChatMenuTreeResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateChatMenuTreeRequest,
                      option: Optional[RequestOption] = None) -> CreateChatMenuTreeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateChatMenuTreeResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteChatMenuTreeRequest,
               option: Optional[RequestOption] = None) -> DeleteChatMenuTreeResponse:
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
        response: DeleteChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteChatMenuTreeResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteChatMenuTreeRequest,
                      option: Optional[RequestOption] = None) -> DeleteChatMenuTreeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteChatMenuTreeResponse)
        response.raw = resp

        return response

    def get(self, request: GetChatMenuTreeRequest, option: Optional[RequestOption] = None) -> GetChatMenuTreeResponse:
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
        response: GetChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetChatMenuTreeResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetChatMenuTreeRequest,
                   option: Optional[RequestOption] = None) -> GetChatMenuTreeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetChatMenuTreeResponse)
        response.raw = resp

        return response

    def sort(self, request: SortChatMenuTreeRequest,
             option: Optional[RequestOption] = None) -> SortChatMenuTreeResponse:
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
        response: SortChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), SortChatMenuTreeResponse)
        response.raw = resp

        return response

    async def asort(self, request: SortChatMenuTreeRequest,
                    option: Optional[RequestOption] = None) -> SortChatMenuTreeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: SortChatMenuTreeResponse = JSON.unmarshal(str(resp.content, UTF_8), SortChatMenuTreeResponse)
        response.raw = resp

        return response
