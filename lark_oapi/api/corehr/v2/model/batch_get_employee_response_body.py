# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .employee import Employee


class BatchGetEmployeeResponseBody(object):
    _types = {
        "items": List[Employee],
    }

    def __init__(self, d=None):
        self.items: Optional[List[Employee]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BatchGetEmployeeResponseBodyBuilder":
        return BatchGetEmployeeResponseBodyBuilder()


class BatchGetEmployeeResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._batch_get_employee_response_body = BatchGetEmployeeResponseBody()

    def items(self, items: List[Employee]) -> "BatchGetEmployeeResponseBodyBuilder":
        self._batch_get_employee_response_body.items = items
        return self

    def build(self) -> "BatchGetEmployeeResponseBody":
        return self._batch_get_employee_response_body
