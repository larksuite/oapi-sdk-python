# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core import JSON
from lark_oapi.core.const import UTF_8, CONTENT_TYPE, APPLICATION_JSON
from lark_oapi.core.http import Transport
from lark_oapi.core.model import Config, RequestOption, RawResponse
from lark_oapi.core.token import verify
from ..model.create_app_access_token_request import CreateAppAccessTokenRequest
from ..model.create_app_access_token_response import CreateAppAccessTokenResponse
from ..model.internal_app_access_token_request import InternalAppAccessTokenRequest
from ..model.internal_app_access_token_response import InternalAppAccessTokenResponse


class AppAccessToken(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def create(self, request: CreateAppAccessTokenRequest,
               option: Optional[RequestOption] = None) -> CreateAppAccessTokenResponse:
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
        response: CreateAppAccessTokenResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateAppAccessTokenResponse)
        response.raw = resp

        return response

    async def acreate(self, request: CreateAppAccessTokenRequest,
                      option: Optional[RequestOption] = None) -> CreateAppAccessTokenResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: CreateAppAccessTokenResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateAppAccessTokenResponse)
        response.raw = resp

        return response

    def internal(self, request: InternalAppAccessTokenRequest,
                 option: Optional[RequestOption] = None) -> InternalAppAccessTokenResponse:
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
        response: InternalAppAccessTokenResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  InternalAppAccessTokenResponse)
        response.raw = resp

        return response

    async def ainternal(self, request: InternalAppAccessTokenRequest,
                        option: Optional[RequestOption] = None) -> InternalAppAccessTokenResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: InternalAppAccessTokenResponse = JSON.unmarshal(str(resp.content, UTF_8),
                                                                  InternalAppAccessTokenResponse)
        response.raw = resp

        return response