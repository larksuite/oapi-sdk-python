# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .sort import Sort
from .filter_info import FilterInfo


class SearchAppTableRecordRequestBody(object):
    _types = {
        "view_id": str,
        "field_names": List[str],
        "sort": List[Sort],
        "filter": FilterInfo,
        "automatic_fields": bool,
    }

    def __init__(self, d=None):
        self.view_id: Optional[str] = None
        self.field_names: Optional[List[str]] = None
        self.sort: Optional[List[Sort]] = None
        self.filter: Optional[FilterInfo] = None
        self.automatic_fields: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchAppTableRecordRequestBodyBuilder":
        return SearchAppTableRecordRequestBodyBuilder()


class SearchAppTableRecordRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._search_app_table_record_request_body = SearchAppTableRecordRequestBody()

    def view_id(self, view_id: str) -> "SearchAppTableRecordRequestBodyBuilder":
        self._search_app_table_record_request_body.view_id = view_id
        return self

    def field_names(self, field_names: List[str]) -> "SearchAppTableRecordRequestBodyBuilder":
        self._search_app_table_record_request_body.field_names = field_names
        return self

    def sort(self, sort: List[Sort]) -> "SearchAppTableRecordRequestBodyBuilder":
        self._search_app_table_record_request_body.sort = sort
        return self

    def filter(self, filter: FilterInfo) -> "SearchAppTableRecordRequestBodyBuilder":
        self._search_app_table_record_request_body.filter = filter
        return self

    def automatic_fields(self, automatic_fields: bool) -> "SearchAppTableRecordRequestBodyBuilder":
        self._search_app_table_record_request_body.automatic_fields = automatic_fields
        return self

    def build(self) -> "SearchAppTableRecordRequestBody":
        return self._search_app_table_record_request_body
