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
from ..model.create_pin_request import CreatePinRequest
from ..model.create_pin_response import CreatePinResponse
from ..model.delete_pin_request import DeletePinRequest
from ..model.delete_pin_response import DeletePinResponse
from ..model.list_pin_request import ListPinRequest
from ..model.list_pin_response import ListPinResponse


class Pin(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreatePinRequest, option: Optional[RequestOption] = None) -> CreatePinResponse:
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
        response: CreatePinResponse = JSON.unmarshal(str(resp.content, UTF_8), CreatePinResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreatePinRequest, option: Optional[RequestOption] = None) -> CreatePinResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreatePinResponse = JSON.unmarshal(str(resp.content, UTF_8), CreatePinResponse)
        response.raw = resp

        return response

    def delete(self, request: DeletePinRequest, option: Optional[RequestOption] = None) -> DeletePinResponse:
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
        response: DeletePinResponse = JSON.unmarshal(str(resp.content, UTF_8), DeletePinResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeletePinRequest, option: Optional[RequestOption] = None) -> DeletePinResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeletePinResponse = JSON.unmarshal(str(resp.content, UTF_8), DeletePinResponse)
        response.raw = resp

        return response

    def list(self, request: ListPinRequest, option: Optional[RequestOption] = None) -> ListPinResponse:
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
        response: ListPinResponse = JSON.unmarshal(str(resp.content, UTF_8), ListPinResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListPinRequest, option: Optional[RequestOption] = None) -> ListPinResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListPinResponse = JSON.unmarshal(str(resp.content, UTF_8), ListPinResponse)
        response.raw = resp

        return response
