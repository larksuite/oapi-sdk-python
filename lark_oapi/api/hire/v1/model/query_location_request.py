# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .query_location_request_body import QueryLocationRequestBody


class QueryLocationRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_token: Optional[str] = None
        self.page_size: Optional[int] = None
        self.request_body: Optional[QueryLocationRequestBody] = None

    @staticmethod
    def builder() -> "QueryLocationRequestBuilder":
        return QueryLocationRequestBuilder()


class QueryLocationRequestBuilder(object):

    def __init__(self) -> None:
        query_location_request = QueryLocationRequest()
        query_location_request.http_method = HttpMethod.POST
        query_location_request.uri = "/open-apis/hire/v1/locations/query"
        query_location_request.token_types = {AccessTokenType.TENANT}
        self._query_location_request: QueryLocationRequest = query_location_request

    def page_token(self, page_token: str) -> "QueryLocationRequestBuilder":
        self._query_location_request.page_token = page_token
        self._query_location_request.add_query("page_token", page_token)
        return self

    def page_size(self, page_size: int) -> "QueryLocationRequestBuilder":
        self._query_location_request.page_size = page_size
        self._query_location_request.add_query("page_size", page_size)
        return self

    def request_body(self, request_body: QueryLocationRequestBody) -> "QueryLocationRequestBuilder":
        self._query_location_request.request_body = request_body
        self._query_location_request.body = request_body
        return self

    def build(self) -> QueryLocationRequest:
        return self._query_location_request