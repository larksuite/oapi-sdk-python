from typing import *

from lark_oapi.core import HttpMethod, AccessTokenType


class BaseRequest(object):
    def __init__(self) -> None:
        self.http_method: Optional[HttpMethod] = None
        self.uri: Optional[str] = None
        self.token_types: Set[AccessTokenType] = set()
        self.paths: Dict[str, str] = {}
        self.queries: Dict[str, str] = {}
        self.headers: Dict[str, str] = {}
        self.body: Any = None

    @staticmethod
    def builder() -> "BaseRequestBuilder":
        return BaseRequestBuilder()


class BaseRequestBuilder(object):

    def __init__(self, base_request: BaseRequest = BaseRequest()) -> None:
        self._base_request: BaseRequest = base_request

    def http_method(self, http_method: HttpMethod) -> "BaseRequestBuilder":
        self._base_request.http_method = http_method
        return self

    def uri(self, uri: str) -> "BaseRequestBuilder":
        self._base_request.uri = uri
        return self

    def token_types(self, token_types: Set[AccessTokenType]) -> "BaseRequestBuilder":
        self._base_request.token_types = token_types
        return self

    def paths(self, paths: Dict[str, str]) -> "BaseRequestBuilder":
        self._base_request.paths = paths
        return self

    def queries(self, queries: Dict[str, str]) -> "BaseRequestBuilder":
        self._base_request.queries = queries
        return self

    def headers(self, headers: Dict[str, str]) -> "BaseRequestBuilder":
        self._base_request.headers = headers
        return self

    def body(self, body: Any) -> "BaseRequestBuilder":
        self._base_request.body = body
        return self

    def build(self) -> BaseRequest:
        return self._base_request
