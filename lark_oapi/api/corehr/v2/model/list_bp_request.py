# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class ListBpRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.user_id_type: Optional[str] = None
        self.department_id_type: Optional[str] = None

    @staticmethod
    def builder() -> "ListBpRequestBuilder":
        return ListBpRequestBuilder()


class ListBpRequestBuilder(object):

    def __init__(self) -> None:
        list_bp_request = ListBpRequest()
        list_bp_request.http_method = HttpMethod.GET
        list_bp_request.uri = "/open-apis/corehr/v2/bps"
        list_bp_request.token_types = {AccessTokenType.TENANT}
        self._list_bp_request: ListBpRequest = list_bp_request

    def page_size(self, page_size: int) -> "ListBpRequestBuilder":
        self._list_bp_request.page_size = page_size
        self._list_bp_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "ListBpRequestBuilder":
        self._list_bp_request.page_token = page_token
        self._list_bp_request.add_query("page_token", page_token)
        return self

    def user_id_type(self, user_id_type: str) -> "ListBpRequestBuilder":
        self._list_bp_request.user_id_type = user_id_type
        self._list_bp_request.add_query("user_id_type", user_id_type)
        return self

    def department_id_type(self, department_id_type: str) -> "ListBpRequestBuilder":
        self._list_bp_request.department_id_type = department_id_type
        self._list_bp_request.add_query("department_id_type", department_id_type)
        return self

    def build(self) -> ListBpRequest:
        return self._list_bp_request
