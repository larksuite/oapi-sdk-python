# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .employee_type_enum import EmployeeTypeEnum


class ListEmployeeTypeEnumResponseBody(object):
    _types = {
        "items": List[EmployeeTypeEnum],
        "has_more": bool,
        "page_token": str,
    }

    def __init__(self, d=None):
        self.items: Optional[List[EmployeeTypeEnum]] = None
        self.has_more: Optional[bool] = None
        self.page_token: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ListEmployeeTypeEnumResponseBodyBuilder":
        return ListEmployeeTypeEnumResponseBodyBuilder()


class ListEmployeeTypeEnumResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._list_employee_type_enum_response_body = ListEmployeeTypeEnumResponseBody()

    def items(self, items: List[EmployeeTypeEnum]) -> "ListEmployeeTypeEnumResponseBodyBuilder":
        self._list_employee_type_enum_response_body.items = items
        return self

    def has_more(self, has_more: bool) -> "ListEmployeeTypeEnumResponseBodyBuilder":
        self._list_employee_type_enum_response_body.has_more = has_more
        return self

    def page_token(self, page_token: str) -> "ListEmployeeTypeEnumResponseBodyBuilder":
        self._list_employee_type_enum_response_body.page_token = page_token
        return self

    def build(self) -> "ListEmployeeTypeEnumResponseBody":
        return self._list_employee_type_enum_response_body