# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from .department_leader import DepartmentLeader
from .department_status import DepartmentStatus
from .user_id import UserId


class DepartmentEvent(object):
    _types = {
        "name": str,
        "parent_department_id": str,
        "department_id": str,
        "open_department_id": str,
        "leader_user_id": str,
        "chat_id": str,
        "order": int,
        "status": DepartmentStatus,
        "leaders": List[DepartmentLeader],
        "department_hrbps": List[UserId],
    }

    def __init__(self, d=None):
        self.name: Optional[str] = None
        self.parent_department_id: Optional[str] = None
        self.department_id: Optional[str] = None
        self.open_department_id: Optional[str] = None
        self.leader_user_id: Optional[str] = None
        self.chat_id: Optional[str] = None
        self.order: Optional[int] = None
        self.status: Optional[DepartmentStatus] = None
        self.leaders: Optional[List[DepartmentLeader]] = None
        self.department_hrbps: Optional[List[UserId]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DepartmentEventBuilder":
        return DepartmentEventBuilder()


class DepartmentEventBuilder(object):
    def __init__(self) -> None:
        self._department_event = DepartmentEvent()

    def name(self, name: str) -> "DepartmentEventBuilder":
        self._department_event.name = name
        return self

    def parent_department_id(self, parent_department_id: str) -> "DepartmentEventBuilder":
        self._department_event.parent_department_id = parent_department_id
        return self

    def department_id(self, department_id: str) -> "DepartmentEventBuilder":
        self._department_event.department_id = department_id
        return self

    def open_department_id(self, open_department_id: str) -> "DepartmentEventBuilder":
        self._department_event.open_department_id = open_department_id
        return self

    def leader_user_id(self, leader_user_id: str) -> "DepartmentEventBuilder":
        self._department_event.leader_user_id = leader_user_id
        return self

    def chat_id(self, chat_id: str) -> "DepartmentEventBuilder":
        self._department_event.chat_id = chat_id
        return self

    def order(self, order: int) -> "DepartmentEventBuilder":
        self._department_event.order = order
        return self

    def status(self, status: DepartmentStatus) -> "DepartmentEventBuilder":
        self._department_event.status = status
        return self

    def leaders(self, leaders: List[DepartmentLeader]) -> "DepartmentEventBuilder":
        self._department_event.leaders = leaders
        return self

    def department_hrbps(self, department_hrbps: List[UserId]) -> "DepartmentEventBuilder":
        self._department_event.department_hrbps = department_hrbps
        return self

    def build(self) -> "DepartmentEvent":
        return self._department_event
