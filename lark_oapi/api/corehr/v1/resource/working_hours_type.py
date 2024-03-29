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
from ..model.create_working_hours_type_request import CreateWorkingHoursTypeRequest
from ..model.create_working_hours_type_response import CreateWorkingHoursTypeResponse
from ..model.delete_working_hours_type_request import DeleteWorkingHoursTypeRequest
from ..model.delete_working_hours_type_response import DeleteWorkingHoursTypeResponse
from ..model.get_working_hours_type_request import GetWorkingHoursTypeRequest
from ..model.get_working_hours_type_response import GetWorkingHoursTypeResponse
from ..model.list_working_hours_type_request import ListWorkingHoursTypeRequest
from ..model.list_working_hours_type_response import ListWorkingHoursTypeResponse
from ..model.patch_working_hours_type_request import PatchWorkingHoursTypeRequest
from ..model.patch_working_hours_type_response import PatchWorkingHoursTypeResponse


class WorkingHoursType(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateWorkingHoursTypeRequest,
               option: Optional[RequestOption] = None) -> CreateWorkingHoursTypeResponse:
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
        response: CreateWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  CreateWorkingHoursTypeResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateWorkingHoursTypeRequest,
                      option: Optional[RequestOption] = None) -> CreateWorkingHoursTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  CreateWorkingHoursTypeResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteWorkingHoursTypeRequest,
               option: Optional[RequestOption] = None) -> DeleteWorkingHoursTypeResponse:
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
        response: DeleteWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  DeleteWorkingHoursTypeResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteWorkingHoursTypeRequest,
                      option: Optional[RequestOption] = None) -> DeleteWorkingHoursTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  DeleteWorkingHoursTypeResponse)
        response.raw = resp

        return response

    def get(self, request: GetWorkingHoursTypeRequest,
            option: Optional[RequestOption] = None) -> GetWorkingHoursTypeResponse:
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
        response: GetWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetWorkingHoursTypeResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetWorkingHoursTypeRequest,
                   option: Optional[RequestOption] = None) -> GetWorkingHoursTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), GetWorkingHoursTypeResponse)
        response.raw = resp

        return response

    def list(self, request: ListWorkingHoursTypeRequest,
             option: Optional[RequestOption] = None) -> ListWorkingHoursTypeResponse:
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
        response: ListWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), ListWorkingHoursTypeResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListWorkingHoursTypeRequest,
                    option: Optional[RequestOption] = None) -> ListWorkingHoursTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8), ListWorkingHoursTypeResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchWorkingHoursTypeRequest,
              option: Optional[RequestOption] = None) -> PatchWorkingHoursTypeResponse:
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
        response: PatchWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                 PatchWorkingHoursTypeResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchWorkingHoursTypeRequest,
                     option: Optional[RequestOption] = None) -> PatchWorkingHoursTypeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchWorkingHoursTypeResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                 PatchWorkingHoursTypeResponse)
        response.raw = resp

        return response
