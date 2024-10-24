# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class QueryRecentChangeDepartmentRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.page_size: Optional[int] = None
        self.page_token: Optional[str] = None
        self.start_date: Optional[str] = None
        self.end_date: Optional[str] = None
        self.department_id_type: Optional[str] = None

    @staticmethod
    def builder() -> "QueryRecentChangeDepartmentRequestBuilder":
        return QueryRecentChangeDepartmentRequestBuilder()


class QueryRecentChangeDepartmentRequestBuilder(object):

    def __init__(self) -> None:
        query_recent_change_department_request = QueryRecentChangeDepartmentRequest()
        query_recent_change_department_request.http_method = HttpMethod.GET
        query_recent_change_department_request.uri = "/open-apis/corehr/v2/departments/query_recent_change"
        query_recent_change_department_request.token_types = {AccessTokenType.TENANT}
        self._query_recent_change_department_request: QueryRecentChangeDepartmentRequest = query_recent_change_department_request

    def page_size(self, page_size: int) -> "QueryRecentChangeDepartmentRequestBuilder":
        self._query_recent_change_department_request.page_size = page_size
        self._query_recent_change_department_request.add_query("page_size", page_size)
        return self

    def page_token(self, page_token: str) -> "QueryRecentChangeDepartmentRequestBuilder":
        self._query_recent_change_department_request.page_token = page_token
        self._query_recent_change_department_request.add_query("page_token", page_token)
        return self

    def start_date(self, start_date: str) -> "QueryRecentChangeDepartmentRequestBuilder":
        self._query_recent_change_department_request.start_date = start_date
        self._query_recent_change_department_request.add_query("start_date", start_date)
        return self

    def end_date(self, end_date: str) -> "QueryRecentChangeDepartmentRequestBuilder":
        self._query_recent_change_department_request.end_date = end_date
        self._query_recent_change_department_request.add_query("end_date", end_date)
        return self

    def department_id_type(self, department_id_type: str) -> "QueryRecentChangeDepartmentRequestBuilder":
        self._query_recent_change_department_request.department_id_type = department_id_type
        self._query_recent_change_department_request.add_query("department_id_type", department_id_type)
        return self

    def build(self) -> QueryRecentChangeDepartmentRequest:
        return self._query_recent_change_department_request