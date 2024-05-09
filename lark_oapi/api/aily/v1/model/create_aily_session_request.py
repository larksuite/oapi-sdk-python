# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .create_aily_session_request_body import CreateAilySessionRequestBody


class CreateAilySessionRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.request_body: Optional[CreateAilySessionRequestBody] = None

    @staticmethod
    def builder() -> "CreateAilySessionRequestBuilder":
        return CreateAilySessionRequestBuilder()


class CreateAilySessionRequestBuilder(object):

    def __init__(self) -> None:
        create_aily_session_request = CreateAilySessionRequest()
        create_aily_session_request.http_method = HttpMethod.POST
        create_aily_session_request.uri = "/open-apis/aily/v1/sessions"
        create_aily_session_request.token_types = {AccessTokenType.USER}
        self._create_aily_session_request: CreateAilySessionRequest = create_aily_session_request

    def request_body(self, request_body: CreateAilySessionRequestBody) -> "CreateAilySessionRequestBuilder":
        self._create_aily_session_request.request_body = request_body
        self._create_aily_session_request.body = request_body
        return self

    def build(self) -> CreateAilySessionRequest:
        return self._create_aily_session_request