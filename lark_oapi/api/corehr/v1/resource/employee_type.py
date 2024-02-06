# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core import JSON
from lark_oapi.core.const import UTF_8, CONTENT_TYPE, APPLICATION_JSON
from lark_oapi.core.http import Transport
from lark_oapi.core.model import Config, RequestOption, RawResponse
from lark_oapi.core.token import verify
from ..model.create_employee_type_request import CreateEmployeeTypeRequest
from ..model.create_employee_type_response import CreateEmployeeTypeResponse
from ..model.delete_employee_type_request import DeleteEmployeeTypeRequest
from ..model.delete_employee_type_response import DeleteEmployeeTypeResponse
from ..model.get_employee_type_request import GetEmployeeTypeRequest
from ..model.get_employee_type_response import GetEmployeeTypeResponse
from ..model.list_employee_type_request import ListEmployeeTypeRequest
from ..model.list_employee_type_response import ListEmployeeTypeResponse
from ..model.patch_employee_type_request import PatchEmployeeTypeRequest
from ..model.patch_employee_type_response import PatchEmployeeTypeResponse


class EmployeeType(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateEmployeeTypeRequest,
               option: Optional[RequestOption] = None) -> CreateEmployeeTypeResponse:
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
        response: CreateEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateEmployeeTypeResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateEmployeeTypeRequest,
                      option: Optional[RequestOption] = None) -> CreateEmployeeTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateEmployeeTypeResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteEmployeeTypeRequest,
               option: Optional[RequestOption] = None) -> DeleteEmployeeTypeResponse:
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
        response: DeleteEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteEmployeeTypeResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteEmployeeTypeRequest,
                      option: Optional[RequestOption] = None) -> DeleteEmployeeTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteEmployeeTypeResponse)
        response.raw = resp

        return response

    def get(self, request: GetEmployeeTypeRequest, option: Optional[RequestOption] = None) -> GetEmployeeTypeResponse:
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
        response: GetEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetEmployeeTypeResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetEmployeeTypeRequest,
                   option: Optional[RequestOption] = None) -> GetEmployeeTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetEmployeeTypeResponse)
        response.raw = resp

        return response

    def list(self, request: ListEmployeeTypeRequest,
             option: Optional[RequestOption] = None) -> ListEmployeeTypeResponse:
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
        response: ListEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), ListEmployeeTypeResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListEmployeeTypeRequest,
                    option: Optional[RequestOption] = None) -> ListEmployeeTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), ListEmployeeTypeResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchEmployeeTypeRequest,
              option: Optional[RequestOption] = None) -> PatchEmployeeTypeResponse:
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
        response: PatchEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchEmployeeTypeResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchEmployeeTypeRequest,
                     option: Optional[RequestOption] = None) -> PatchEmployeeTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchEmployeeTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchEmployeeTypeResponse)
        response.raw = resp

        return response