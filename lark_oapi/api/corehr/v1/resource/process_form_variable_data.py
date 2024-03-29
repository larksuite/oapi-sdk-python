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
from ..model.get_process_form_variable_data_request import GetProcessFormVariableDataRequest
from ..model.get_process_form_variable_data_response import GetProcessFormVariableDataResponse


class ProcessFormVariableData(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def get(self, request: GetProcessFormVariableDataRequest,
            option: Optional[RequestOption] = None) -> GetProcessFormVariableDataResponse:
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
        response: GetProcessFormVariableDataResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                      GetProcessFormVariableDataResponse)
        response.raw = resp

        return response

    async def aget(self, request: GetProcessFormVariableDataRequest,
                   option: Optional[RequestOption] = None) -> GetProcessFormVariableDataResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: GetProcessFormVariableDataResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                      GetProcessFormVariableDataResponse)
        response.raw = resp

        return response
