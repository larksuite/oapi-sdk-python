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
from ..model.get_employee_request import GetEmployeeRequest
from ..model.get_employee_response import GetEmployeeResponse
from ..model.get_by_application_employee_request import GetByApplicationEmployeeRequest
from ..model.get_by_application_employee_response import GetByApplicationEmployeeResponse
from ..model.patch_employee_request import PatchEmployeeRequest
from ..model.patch_employee_response import PatchEmployeeResponse


class Employee(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def get(self, request: GetEmployeeRequest, option: Optional[RequestOption] = None) -> GetEmployeeResponse:
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
        response: GetEmployeeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetEmployeeResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetEmployeeRequest, option: Optional[RequestOption] = None) -> GetEmployeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetEmployeeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetEmployeeResponse)
        response.raw = resp

        return response

    def get_by_application(self, request: GetByApplicationEmployeeRequest,
                           option: Optional[RequestOption] = None) -> GetByApplicationEmployeeResponse:
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
        response: GetByApplicationEmployeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                    GetByApplicationEmployeeResponse)
        response.raw = resp

        return response

    async def aget_by_application(self, request: GetByApplicationEmployeeRequest,
                                  option: Optional[RequestOption] = None) -> GetByApplicationEmployeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetByApplicationEmployeeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                    GetByApplicationEmployeeResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchEmployeeRequest, option: Optional[RequestOption] = None) -> PatchEmployeeResponse:
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
        response: PatchEmployeeResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchEmployeeResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchEmployeeRequest,
                     option: Optional[RequestOption] = None) -> PatchEmployeeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchEmployeeResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchEmployeeResponse)
        response.raw = resp

        return response
