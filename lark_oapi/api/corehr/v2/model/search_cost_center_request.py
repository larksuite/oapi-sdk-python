# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .search_cost_center_request_body import SearchCostCenterRequestBody


class SearchCostCenterRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.user_id_type: Optional[str] = None
        self.request_body: Optional[SearchCostCenterRequestBody] = None

    @staticmethod
    def builder() -> "SearchCostCenterRequestBuilder":
        return SearchCostCenterRequestBuilder()


class SearchCostCenterRequestBuilder(object):

    def __init__(self) -> None:
        search_cost_center_request = SearchCostCenterRequest()
        search_cost_center_request.http_method = HttpMethod.POST
        search_cost_center_request.uri = "/open-apis/corehr/v2/cost_centers/search"
        search_cost_center_request.token_types = {AccessTokenType.TENANT}
        self._search_cost_center_request: SearchCostCenterRequest = search_cost_center_request

    def page_size(self, page_size: int) -> "SearchCostCenterRequestBuilder":
        self._search_cost_center_request.page_size = page_size
        self._search_cost_center_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "SearchCostCenterRequestBuilder":
        self._search_cost_center_request.page_token = page_token
        self._search_cost_center_request.add_query("page_token", page_token)
        return self

    def user_id_type(self, user_id_type: str) -> "SearchCostCenterRequestBuilder":
        self._search_cost_center_request.user_id_type = user_id_type
        self._search_cost_center_request.add_query("user_id_type", user_id_type)
        return self

    def request_body(self, request_body: SearchCostCenterRequestBody) -> "SearchCostCenterRequestBuilder":
        self._search_cost_center_request.request_body = request_body
        self._search_cost_center_request.body = request_body
        return self

    def build(self) -> SearchCostCenterRequest:
        return self._search_cost_center_request
