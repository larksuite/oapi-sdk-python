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
from ..model.create_task_follower_request import CreateTaskFollowerRequest
from ..model.create_task_follower_response import CreateTaskFollowerResponse
from ..model.delete_task_follower_request import DeleteTaskFollowerRequest
from ..model.delete_task_follower_response import DeleteTaskFollowerResponse
from ..model.list_task_follower_request import ListTaskFollowerRequest
from ..model.list_task_follower_response import ListTaskFollowerResponse


class TaskFollower(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateTaskFollowerRequest,
               option: Optional[RequestOption] = None) -> CreateTaskFollowerResponse:
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
        response: CreateTaskFollowerResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateTaskFollowerResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateTaskFollowerRequest,
                      option: Optional[RequestOption] = None) -> CreateTaskFollowerResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateTaskFollowerResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateTaskFollowerResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteTaskFollowerRequest,
               option: Optional[RequestOption] = None) -> DeleteTaskFollowerResponse:
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
        response: DeleteTaskFollowerResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteTaskFollowerResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteTaskFollowerRequest,
                      option: Optional[RequestOption] = None) -> DeleteTaskFollowerResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteTaskFollowerResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteTaskFollowerResponse)
        response.raw = resp

        return response

    def list(self, request: ListTaskFollowerRequest,
             option: Optional[RequestOption] = None) -> ListTaskFollowerResponse:
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
        response: ListTaskFollowerResponse = JSON.unmarshal(str(resp.content, UTF_8), ListTaskFollowerResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListTaskFollowerRequest,
                    option: Optional[RequestOption] = None) -> ListTaskFollowerResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListTaskFollowerResponse = JSON.unmarshal(str(resp.content, UTF_8), ListTaskFollowerResponse)
        response.raw = resp

        return response
