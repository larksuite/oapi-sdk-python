# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .cost_center import CostCenter


class PatchCostCenterResponseBody(object):
    _types = {
        "cost_center": CostCenter,
    }

    def __init__(self, d=None):
        self.cost_center: Optional[CostCenter] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PatchCostCenterResponseBodyBuilder":
        return PatchCostCenterResponseBodyBuilder()


class PatchCostCenterResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._patch_cost_center_response_body = PatchCostCenterResponseBody()

    def cost_center(self, cost_center: CostCenter) -> "PatchCostCenterResponseBodyBuilder":
        self._patch_cost_center_response_body.cost_center = cost_center
        return self

    def build(self) -> "PatchCostCenterResponseBody":
        return self._patch_cost_center_response_body
