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
from ..model.create_moto_request import CreateMotoRequest
from ..model.create_moto_response import CreateMotoResponse
from ..model.get_moto_request import GetMotoRequest
from ..model.get_moto_response import GetMotoResponse
from ..model.list_moto_request import ListMotoRequest
from ..model.list_moto_response import ListMotoResponse


class Moto(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateMotoRequest, option: Optional[RequestOption] = None) -> CreateMotoResponse:
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
        response: CreateMotoResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateMotoResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateMotoRequest, option: Optional[RequestOption] = None) -> CreateMotoResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateMotoResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateMotoResponse)
        response.raw = resp

        return response

    def get(self, request: GetMotoRequest, option: Optional[RequestOption] = None) -> GetMotoResponse:
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
        response: GetMotoResponse = JSON.unmarshal(str(resp.content, UTF_8), GetMotoResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetMotoRequest, option: Optional[RequestOption] = None) -> GetMotoResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetMotoResponse = JSON.unmarshal(str(resp.content, UTF_8), GetMotoResponse)
        response.raw = resp

        return response

    def list(self, request: ListMotoRequest, option: Optional[RequestOption] = None) -> ListMotoResponse:
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
        response: ListMotoResponse = JSON.unmarshal(str(resp.content, UTF_8), ListMotoResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListMotoRequest, option: Optional[RequestOption] = None) -> ListMotoResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListMotoResponse = JSON.unmarshal(str(resp.content, UTF_8), ListMotoResponse)
        response.raw = resp

        return response
