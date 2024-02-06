# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class UserOkrObjectiveAlignedObjectiveOwner(object):
    _types = {
        "open_id": str,
        "employee_id": str,
        "employee_no": str,
        "union_id": str,
        "name": str,
    }

    def __init__(self, d=None):
        self.open_id: Optional[str] = None
        self.employee_id: Optional[str] = None
        self.employee_no: Optional[str] = None
        self.union_id: Optional[str] = None
        self.name: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UserOkrObjectiveAlignedObjectiveOwnerBuilder":
        return UserOkrObjectiveAlignedObjectiveOwnerBuilder()


class UserOkrObjectiveAlignedObjectiveOwnerBuilder(object):
    def __init__(self) -> None:
        self._user_okr_objective_aligned_objective_owner = UserOkrObjectiveAlignedObjectiveOwner()

    def open_id(self, open_id: str) -> "UserOkrObjectiveAlignedObjectiveOwnerBuilder":
        self._user_okr_objective_aligned_objective_owner.open_id = open_id
        return self

    def employee_id(self, employee_id: str) -> "UserOkrObjectiveAlignedObjectiveOwnerBuilder":
        self._user_okr_objective_aligned_objective_owner.employee_id = employee_id
        return self

    def employee_no(self, employee_no: str) -> "UserOkrObjectiveAlignedObjectiveOwnerBuilder":
        self._user_okr_objective_aligned_objective_owner.employee_no = employee_no
        return self

    def union_id(self, union_id: str) -> "UserOkrObjectiveAlignedObjectiveOwnerBuilder":
        self._user_okr_objective_aligned_objective_owner.union_id = union_id
        return self

    def name(self, name: str) -> "UserOkrObjectiveAlignedObjectiveOwnerBuilder":
        self._user_okr_objective_aligned_objective_owner.name = name
        return self

    def build(self) -> "UserOkrObjectiveAlignedObjectiveOwner":
        return self._user_okr_objective_aligned_objective_owner