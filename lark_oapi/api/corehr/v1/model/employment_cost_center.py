# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .cost_center import CostCenter


class EmploymentCostCenter(object):
    _types = {
        "employment_id": str,
        "cost_center": List[CostCenter],
    }

    def __init__(self, d=None):
        self.employment_id: Optional[str] = None
        self.cost_center: Optional[List[CostCenter]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "EmploymentCostCenterBuilder":
        return EmploymentCostCenterBuilder()


class EmploymentCostCenterBuilder(object):
    def __init__(self) -> None:
        self._employment_cost_center = EmploymentCostCenter()

    def employment_id(self, employment_id: str) -> "EmploymentCostCenterBuilder":
        self._employment_cost_center.employment_id = employment_id
        return self

    def cost_center(self, cost_center: List[CostCenter]) -> "EmploymentCostCenterBuilder":
        self._employment_cost_center.cost_center = cost_center
        return self

    def build(self) -> "EmploymentCostCenter":
        return self._employment_cost_center