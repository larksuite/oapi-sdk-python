# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class BatchGetEmployeesBpRequestBody(object):
    _types = {
        "employment_ids": List[str],
        "get_all": bool,
    }

    def __init__(self, d=None):
        self.employment_ids: Optional[List[str]] = None
        self.get_all: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BatchGetEmployeesBpRequestBodyBuilder":
        return BatchGetEmployeesBpRequestBodyBuilder()


class BatchGetEmployeesBpRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._batch_get_employees_bp_request_body = BatchGetEmployeesBpRequestBody()

    def employment_ids(self, employment_ids: List[str]) -> "BatchGetEmployeesBpRequestBodyBuilder":
        self._batch_get_employees_bp_request_body.employment_ids = employment_ids
        return self

    def get_all(self, get_all: bool) -> "BatchGetEmployeesBpRequestBodyBuilder":
        self._batch_get_employees_bp_request_body.get_all = get_all
        return self

    def build(self) -> "BatchGetEmployeesBpRequestBody":
        return self._batch_get_employees_bp_request_body
