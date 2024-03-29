# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .recognize_business_card_request_body import RecognizeBusinessCardRequestBody


class RecognizeBusinessCardRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.request_body: Optional[RecognizeBusinessCardRequestBody] = None

    @staticmethod
    def builder() -> "RecognizeBusinessCardRequestBuilder":
        return RecognizeBusinessCardRequestBuilder()


class RecognizeBusinessCardRequestBuilder(object):

    def __init__(self) -> None:
        recognize_business_card_request = RecognizeBusinessCardRequest()
        recognize_business_card_request.http_method = HttpMethod.POST
        recognize_business_card_request.uri = "/open-apis/document_ai/v1/business_card/recognize"
        recognize_business_card_request.token_types = {AccessTokenType.TENANT}
        self._recognize_business_card_request: RecognizeBusinessCardRequest = recognize_business_card_request

    def request_body(self, request_body: RecognizeBusinessCardRequestBody) -> "RecognizeBusinessCardRequestBuilder":
        self._recognize_business_card_request.request_body = request_body
        self._recognize_business_card_request.body = request_body
        return self

    def build(self) -> RecognizeBusinessCardRequest:
        return self._recognize_business_card_request
