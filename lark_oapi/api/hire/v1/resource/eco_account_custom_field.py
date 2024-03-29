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
from ..model.batch_delete_eco_account_custom_field_request import BatchDeleteEcoAccountCustomFieldRequest
from ..model.batch_delete_eco_account_custom_field_response import BatchDeleteEcoAccountCustomFieldResponse
from ..model.batch_update_eco_account_custom_field_request import BatchUpdateEcoAccountCustomFieldRequest
from ..model.batch_update_eco_account_custom_field_response import BatchUpdateEcoAccountCustomFieldResponse
from ..model.create_eco_account_custom_field_request import CreateEcoAccountCustomFieldRequest
from ..model.create_eco_account_custom_field_response import CreateEcoAccountCustomFieldResponse


class EcoAccountCustomField(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def batch_delete(self, request: BatchDeleteEcoAccountCustomFieldRequest,
                     option: Optional[RequestOption] = None) -> BatchDeleteEcoAccountCustomFieldResponse:
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
        response: BatchDeleteEcoAccountCustomFieldResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            BatchDeleteEcoAccountCustomFieldResponse)
        response.raw = resp

        return response

    async def abatch_delete(self, request: BatchDeleteEcoAccountCustomFieldRequest,
                            option: Optional[RequestOption] = None) -> BatchDeleteEcoAccountCustomFieldResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: BatchDeleteEcoAccountCustomFieldResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            BatchDeleteEcoAccountCustomFieldResponse)
        response.raw = resp

        return response

    def batch_update(self, request: BatchUpdateEcoAccountCustomFieldRequest,
                     option: Optional[RequestOption] = None) -> BatchUpdateEcoAccountCustomFieldResponse:
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
        response: BatchUpdateEcoAccountCustomFieldResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            BatchUpdateEcoAccountCustomFieldResponse)
        response.raw = resp

        return response

    async def abatch_update(self, request: BatchUpdateEcoAccountCustomFieldRequest,
                            option: Optional[RequestOption] = None) -> BatchUpdateEcoAccountCustomFieldResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: BatchUpdateEcoAccountCustomFieldResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            BatchUpdateEcoAccountCustomFieldResponse)
        response.raw = resp

        return response

    def create(self, request: CreateEcoAccountCustomFieldRequest,
               option: Optional[RequestOption] = None) -> CreateEcoAccountCustomFieldResponse:
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
        response: CreateEcoAccountCustomFieldResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                       CreateEcoAccountCustomFieldResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateEcoAccountCustomFieldRequest,
                      option: Optional[RequestOption] = None) -> CreateEcoAccountCustomFieldResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateEcoAccountCustomFieldResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                       CreateEcoAccountCustomFieldResponse)
        response.raw = resp

        return response
