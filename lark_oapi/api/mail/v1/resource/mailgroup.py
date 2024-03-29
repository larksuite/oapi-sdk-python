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
from ..model.create_mailgroup_request import CreateMailgroupRequest
from ..model.create_mailgroup_response import CreateMailgroupResponse
from ..model.delete_mailgroup_request import DeleteMailgroupRequest
from ..model.delete_mailgroup_response import DeleteMailgroupResponse
from ..model.get_mailgroup_request import GetMailgroupRequest
from ..model.get_mailgroup_response import GetMailgroupResponse
from ..model.list_mailgroup_request import ListMailgroupRequest
from ..model.list_mailgroup_response import ListMailgroupResponse
from ..model.patch_mailgroup_request import PatchMailgroupRequest
from ..model.patch_mailgroup_response import PatchMailgroupResponse
from ..model.update_mailgroup_request import UpdateMailgroupRequest
from ..model.update_mailgroup_response import UpdateMailgroupResponse


class Mailgroup(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateMailgroupRequest,
               option: Optional[RequestOption] = None) -> CreateMailgroupResponse:
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
        response: CreateMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateMailgroupResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateMailgroupRequest,
                      option: Optional[RequestOption] = None) -> CreateMailgroupResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateMailgroupResponse)
        response.raw = resp

        return response

    def delete(self, request: DeleteMailgroupRequest,
               option: Optional[RequestOption] = None) -> DeleteMailgroupResponse:
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
        response: DeleteMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteMailgroupResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteMailgroupRequest,
                      option: Optional[RequestOption] = None) -> DeleteMailgroupResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteMailgroupResponse)
        response.raw = resp

        return response

    def get(self, request: GetMailgroupRequest, option: Optional[RequestOption] = None) -> GetMailgroupResponse:
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
        response: GetMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), GetMailgroupResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetMailgroupRequest, option: Optional[RequestOption] = None) -> GetMailgroupResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), GetMailgroupResponse)
        response.raw = resp

        return response

    def list(self, request: ListMailgroupRequest, option: Optional[RequestOption] = None) -> ListMailgroupResponse:
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
        response: ListMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), ListMailgroupResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListMailgroupRequest,
                    option: Optional[RequestOption] = None) -> ListMailgroupResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), ListMailgroupResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchMailgroupRequest, option: Optional[RequestOption] = None) -> PatchMailgroupResponse:
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
        response: PatchMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchMailgroupResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchMailgroupRequest,
                     option: Optional[RequestOption] = None) -> PatchMailgroupResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchMailgroupResponse)
        response.raw = resp

        return response

    def update(self, request: UpdateMailgroupRequest,
               option: Optional[RequestOption] = None) -> UpdateMailgroupResponse:
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
        response: UpdateMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), UpdateMailgroupResponse)
        response.raw = resp

        return response

    async def aupdate(self, request: UpdateMailgroupRequest,
                      option: Optional[RequestOption] = None) -> UpdateMailgroupResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: UpdateMailgroupResponse = JSON.unmarshal(str(resp.content, UTF_8), UpdateMailgroupResponse)
        response.raw = resp

        return response
