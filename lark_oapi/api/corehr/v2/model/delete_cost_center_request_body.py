# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class DeleteCostCenterRequestBody(object):
    _types = {
        "operation_reason": str,
    }

    def __init__(self, d=None):
        self.operation_reason: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DeleteCostCenterRequestBodyBuilder":
        return DeleteCostCenterRequestBodyBuilder()


class DeleteCostCenterRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._delete_cost_center_request_body = DeleteCostCenterRequestBody()

    def operation_reason(self, operation_reason: str) -> "DeleteCostCenterRequestBodyBuilder":
        self._delete_cost_center_request_body.operation_reason = operation_reason
        return self

    def build(self) -> "DeleteCostCenterRequestBody":
        return self._delete_cost_center_request_body
