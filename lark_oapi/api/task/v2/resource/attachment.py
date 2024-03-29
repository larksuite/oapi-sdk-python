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
from ..model.delete_attachment_request import DeleteAttachmentRequest
from ..model.delete_attachment_response import DeleteAttachmentResponse
from ..model.get_attachment_request import GetAttachmentRequest
from ..model.get_attachment_response import GetAttachmentResponse
from ..model.list_attachment_request import ListAttachmentRequest
from ..model.list_attachment_response import ListAttachmentResponse
from ..model.upload_attachment_request import UploadAttachmentRequest
from ..model.upload_attachment_response import UploadAttachmentResponse


class Attachment(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def delete(self, request: DeleteAttachmentRequest,
               option: Optional[RequestOption] = None) -> DeleteAttachmentResponse:
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
        response: DeleteAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteAttachmentResponse)
        response.raw = resp

        return response

    async def adelete(self, request: DeleteAttachmentRequest,
                      option: Optional[RequestOption] = None) -> DeleteAttachmentResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: DeleteAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), DeleteAttachmentResponse)
        response.raw = resp

        return response

    def get(self, request: GetAttachmentRequest, option: Optional[RequestOption] = None) -> GetAttachmentResponse:
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
        response: GetAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), GetAttachmentResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetAttachmentRequest,
                   option: Optional[RequestOption] = None) -> GetAttachmentResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), GetAttachmentResponse)
        response.raw = resp

        return response

    def list(self, request: ListAttachmentRequest, option: Optional[RequestOption] = None) -> ListAttachmentResponse:
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
        response: ListAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), ListAttachmentResponse)
        response.raw = resp

        return response

    async def alist(self, request: ListAttachmentRequest,
                    option: Optional[RequestOption] = None) -> ListAttachmentResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: ListAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), ListAttachmentResponse)
        response.raw = resp

        return response

    def upload(self, request: UploadAttachmentRequest,
               option: Optional[RequestOption] = None) -> UploadAttachmentResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 添加 content-type
        if request.body is not None:
            form_data = MultipartEncoder(Files.parse_form_data(request.body))
            request.body = form_data
            option.headers[CONTENT_TYPE] = form_data.content_type

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: UploadAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), UploadAttachmentResponse)
        response.raw = resp

        return response

    async def aupload(self, request: UploadAttachmentRequest,
                      option: Optional[RequestOption] = None) -> UploadAttachmentResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 解析文件
        request.files = Files.extract_files(request.body)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: UploadAttachmentResponse = JSON.unmarshal(str(resp.content, UTF_8), UploadAttachmentResponse)
        response.raw = resp

        return response
