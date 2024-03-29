# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class CreateOidcAccessTokenRequestBody(object):
    _types = {
        "grant_type": str,
        "code": str,
    }

    def __init__(self, d=None):
        self.grant_type: Optional[str] = None
        self.code: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateOidcAccessTokenRequestBodyBuilder":
        return CreateOidcAccessTokenRequestBodyBuilder()


class CreateOidcAccessTokenRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._create_oidc_access_token_request_body = CreateOidcAccessTokenRequestBody()

    def grant_type(self, grant_type: str) -> "CreateOidcAccessTokenRequestBodyBuilder":
        self._create_oidc_access_token_request_body.grant_type = grant_type
        return self

    def code(self, code: str) -> "CreateOidcAccessTokenRequestBodyBuilder":
        self._create_oidc_access_token_request_body.code = code
        return self

    def build(self) -> "CreateOidcAccessTokenRequestBody":
        return self._create_oidc_access_token_request_body
