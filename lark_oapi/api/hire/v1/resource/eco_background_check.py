# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core import JSON
from lark_oapi.core.const import UTF_8, CONTENT_TYPE, APPLICATION_JSON
from lark_oapi.core.http import Transport
from lark_oapi.core.model import Config, RequestOption, RawResponse
from lark_oapi.core.token import verify
from ..model.cancel_eco_background_check_request import CancelEcoBackgroundCheckRequest
from ..model.cancel_eco_background_check_response import CancelEcoBackgroundCheckResponse
from ..model.update_progress_eco_background_check_request import UpdateProgressEcoBackgroundCheckRequest
from ..model.update_progress_eco_background_check_response import UpdateProgressEcoBackgroundCheckResponse
from ..model.update_result_eco_background_check_request import UpdateResultEcoBackgroundCheckRequest
from ..model.update_result_eco_background_check_response import UpdateResultEcoBackgroundCheckResponse


class EcoBackgroundCheck(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def cancel(self, request: CancelEcoBackgroundCheckRequest,
               option: Optional[RequestOption] = None) -> CancelEcoBackgroundCheckResponse:
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
        response: CancelEcoBackgroundCheckResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                    CancelEcoBackgroundCheckResponse)
        response.raw = resp

        return response

    async def acancel(self, request: CancelEcoBackgroundCheckRequest,
                      option: Optional[RequestOption] = None) -> CancelEcoBackgroundCheckResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CancelEcoBackgroundCheckResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                    CancelEcoBackgroundCheckResponse)
        response.raw = resp

        return response

    def update_progress(self, request: UpdateProgressEcoBackgroundCheckRequest,
                        option: Optional[RequestOption] = None) -> UpdateProgressEcoBackgroundCheckResponse:
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
        response: UpdateProgressEcoBackgroundCheckResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            UpdateProgressEcoBackgroundCheckResponse)
        response.raw = resp

        return response

    async def aupdate_progress(self, request: UpdateProgressEcoBackgroundCheckRequest,
                               option: Optional[RequestOption] = None) -> UpdateProgressEcoBackgroundCheckResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: UpdateProgressEcoBackgroundCheckResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                            UpdateProgressEcoBackgroundCheckResponse)
        response.raw = resp

        return response

    def update_result(self, request: UpdateResultEcoBackgroundCheckRequest,
                      option: Optional[RequestOption] = None) -> UpdateResultEcoBackgroundCheckResponse:
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
        response: UpdateResultEcoBackgroundCheckResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                          UpdateResultEcoBackgroundCheckResponse)
        response.raw = resp

        return response

    async def aupdate_result(self, request: UpdateResultEcoBackgroundCheckRequest,
                             option: Optional[RequestOption] = None) -> UpdateResultEcoBackgroundCheckResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: UpdateResultEcoBackgroundCheckResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                          UpdateResultEcoBackgroundCheckResponse)
        response.raw = resp

        return response