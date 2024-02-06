# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class UnitDepartment(object):
    _types = {
        "unit_id": str,
        "department_id": str,
    }

    def __init__(self, d=None):
        self.unit_id: Optional[str] = None
        self.department_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UnitDepartmentBuilder":
        return UnitDepartmentBuilder()


class UnitDepartmentBuilder(object):
    def __init__(self) -> None:
        self._unit_department = UnitDepartment()

    def unit_id(self, unit_id: str) -> "UnitDepartmentBuilder":
        self._unit_department.unit_id = unit_id
        return self

    def department_id(self, department_id: str) -> "UnitDepartmentBuilder":
        self._unit_department.department_id = department_id
        return self

    def build(self) -> "UnitDepartment":
        return self._unit_department