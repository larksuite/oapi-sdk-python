# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init


class UserGroup(object):
    _types = {
        "user_group_id": str,
        "name": str,
        "type": int,
        "member_count": int,
        "status": int,
    }

    def __init__(self, d):
        self.user_group_id: Optional[str] = None
        self.name: Optional[str] = None
        self.type: Optional[int] = None
        self.member_count: Optional[int] = None
        self.status: Optional[int] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UserGroupBuilder":
        return UserGroupBuilder()


class UserGroupBuilder(object):
    def __init__(self, user_group: UserGroup = UserGroup({})) -> None:
        self._user_group: UserGroup = user_group
    
    def user_group_id(self, user_group_id: str) -> "UserGroupBuilder":
        self._user_group.user_group_id = user_group_id
        return self
    
    def name(self, name: str) -> "UserGroupBuilder":
        self._user_group.name = name
        return self
    
    def type(self, type: int) -> "UserGroupBuilder":
        self._user_group.type = type
        return self
    
    def member_count(self, member_count: int) -> "UserGroupBuilder":
        self._user_group.member_count = member_count
        return self
    
    def status(self, status: int) -> "UserGroupBuilder":
        self._user_group.status = status
        return self
    
    def build(self) -> "UserGroup":
        return self._user_group