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
from ..model.create_app_table_view_request import CreateAppTableViewRequest
from ..model.create_app_table_view_response import CreateAppTableViewResponse
from ..model.delete_app_table_view_request import DeleteAppTableViewRequest
from ..model.delete_app_table_view_response import DeleteAppTableViewResponse
from ..model.get_app_table_view_request import GetAppTableViewRequest
from ..model.get_app_table_view_response import GetAppTableViewResponse
from ..model.list_app_table_view_request import ListAppTableViewRequest
from ..model.list_app_table_view_response import ListAppTableViewResponse
from ..model.patch_app_table_view_request import PatchAppTableViewRequest
from ..model.patch_app_table_view_response import PatchAppTableViewResponse


class AppTableView(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateAppTableViewRequest,
               option: Optional[RequestOption] = None) -> CreateAppTableViewResponse:
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
        response: CreateAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateAppTableViewResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateAppTableViewRequest,
                      option: Optional[RequestOption] = None) -> CreateAppTableViewResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateAppTableViewResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteAppTableViewRequest,
               option: Optional[RequestOption] = None) -> DeleteAppTableViewResponse:
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
        response: DeleteAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteAppTableViewResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteAppTableViewRequest,
                      option: Optional[RequestOption] = None) -> DeleteAppTableViewResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteAppTableViewResponse)
        response.raw = resp

        return response

    def get(self, request: GetAppTableViewRequest, option: Optional[RequestOption] = None) -> GetAppTableViewResponse:
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
        response: GetAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), GetAppTableViewResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetAppTableViewRequest,
                   option: Optional[RequestOption] = None) -> GetAppTableViewResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), GetAppTableViewResponse)
        response.raw = resp

        return response

    def list(self, request: ListAppTableViewRequest,
             option: Optional[RequestOption] = None) -> ListAppTableViewResponse:
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
        response: ListAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), ListAppTableViewResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListAppTableViewRequest,
                    option: Optional[RequestOption] = None) -> ListAppTableViewResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), ListAppTableViewResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchAppTableViewRequest,
              option: Optional[RequestOption] = None) -> PatchAppTableViewResponse:
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
        response: PatchAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchAppTableViewResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchAppTableViewRequest,
                     option: Optional[RequestOption] = None) -> PatchAppTableViewResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchAppTableViewResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchAppTableViewResponse)
        response.raw = resp

        return response
