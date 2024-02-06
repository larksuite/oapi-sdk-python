# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .custom_fields import CustomFields
from .system_fields import SystemFields


class Employee(object):
    _types = {
        "user_id": str,
        "system_fields": SystemFields,
        "custom_fields": List[CustomFields],
    }

    def __init__(self, d=None):
        self.user_id: Optional[str] = None
        self.system_fields: Optional[SystemFields] = None
        self.custom_fields: Optional[List[CustomFields]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "EmployeeBuilder":
        return EmployeeBuilder()


class EmployeeBuilder(object):
    def __init__(self) -> None:
        self._employee = Employee()

    def user_id(self, user_id: str) -> "EmployeeBuilder":
        self._employee.user_id = user_id
        return self

    def system_fields(self, system_fields: SystemFields) -> "EmployeeBuilder":
        self._employee.system_fields = system_fields
        return self

    def custom_fields(self, custom_fields: List[CustomFields]) -> "EmployeeBuilder":
        self._employee.custom_fields = custom_fields
        return self

    def build(self) -> "Employee":
        return self._employee