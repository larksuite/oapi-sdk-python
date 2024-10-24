# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class TransitTaskPreHireRequestBody(object):
    _types = {
        "task_id": str,
    }

    def __init__(self, d=None):
        self.task_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "TransitTaskPreHireRequestBodyBuilder":
        return TransitTaskPreHireRequestBodyBuilder()


class TransitTaskPreHireRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._transit_task_pre_hire_request_body = TransitTaskPreHireRequestBody()

    def task_id(self, task_id: str) -> "TransitTaskPreHireRequestBodyBuilder":
        self._transit_task_pre_hire_request_body.task_id = task_id
        return self

    def build(self) -> "TransitTaskPreHireRequestBody":
        return self._transit_task_pre_hire_request_body
