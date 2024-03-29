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
from ..model.batch_update_document_block_request import BatchUpdateDocumentBlockRequest
from ..model.batch_update_document_block_response import BatchUpdateDocumentBlockResponse
from ..model.get_document_block_request import GetDocumentBlockRequest
from ..model.get_document_block_response import GetDocumentBlockResponse
from ..model.list_document_block_request import ListDocumentBlockRequest
from ..model.list_document_block_response import ListDocumentBlockResponse
from ..model.patch_document_block_request import PatchDocumentBlockRequest
from ..model.patch_document_block_response import PatchDocumentBlockResponse


class DocumentBlock(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def batch_update(self, request: BatchUpdateDocumentBlockRequest,
                     option: Optional[RequestOption] = None) -> BatchUpdateDocumentBlockResponse:
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
        response: BatchUpdateDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                    BatchUpdateDocumentBlockResponse)
        response.raw = resp

        return response

    async def abatch_update(self, request: BatchUpdateDocumentBlockRequest,
                            option: Optional[RequestOption] = None) -> BatchUpdateDocumentBlockResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: BatchUpdateDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                    BatchUpdateDocumentBlockResponse)
        response.raw = resp

        return response

    def get(self, request: GetDocumentBlockRequest, option: Optional[RequestOption] = None) -> GetDocumentBlockResponse:
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
        response: GetDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8), GetDocumentBlockResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetDocumentBlockRequest,
                   option: Optional[RequestOption] = None) -> GetDocumentBlockResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8), GetDocumentBlockResponse)
        response.raw = resp

        return response

    def list(self, request: ListDocumentBlockRequest,
             option: Optional[RequestOption] = None) -> ListDocumentBlockResponse:
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
        response: ListDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8), ListDocumentBlockResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListDocumentBlockRequest,
                    option: Optional[RequestOption] = None) -> ListDocumentBlockResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8), ListDocumentBlockResponse)
        response.raw = resp

        return response

    def patch(self, request: PatchDocumentBlockRequest,
              option: Optional[RequestOption] = None) -> PatchDocumentBlockResponse:
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
        response: PatchDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchDocumentBlockResponse)
        response.raw = resp

        return response

    async def apatch(self, request: PatchDocumentBlockRequest,
                     option: Optional[RequestOption] = None) -> PatchDocumentBlockResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: PatchDocumentBlockResponse = JSON.unmarshal(str(resp.content, UTF_8), PatchDocumentBlockResponse)
        response.raw = resp

        return response
