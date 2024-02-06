# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest
from .employment_create import EmploymentCreate


class CreateEmploymentRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.client_token: Optional[str] = None
        self.request_body: Optional[EmploymentCreate] = None

    @staticmethod
    def builder() -> "CreateEmploymentRequestBuilder":
        return CreateEmploymentRequestBuilder()


class CreateEmploymentRequestBuilder(object):

    def __init__(self) -> None:
        create_employment_request = CreateEmploymentRequest()
        create_employment_request.http_method = HttpMethod.POST
        create_employment_request.uri = "/open-apis/corehr/v1/employments"
        create_employment_request.token_types = {AccessTokenType.TENANT}
        self._create_employment_request: CreateEmploymentRequest = create_employment_request

    def client_token(self, client_token: str) -> "CreateEmploymentRequestBuilder":
        self._create_employment_request.client_token = client_token
        self._create_employment_request.add_query("client_token", client_token)
        return self

    def request_body(self, request_body: EmploymentCreate) -> "CreateEmploymentRequestBuilder":
        self._create_employment_request.request_body = request_body
        self._create_employment_request.body = request_body
        return self

    def build(self) -> CreateEmploymentRequest:
        return self._create_employment_request