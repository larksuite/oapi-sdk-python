# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class UserShiftGroupsList(object):
    _types = {
        "shift_group_id": str,
        "shift_group_name": str,
        "group_id": str,
        "update_time": str,
    }

    def __init__(self, d=None):
        self.shift_group_id: Optional[str] = None
        self.shift_group_name: Optional[str] = None
        self.group_id: Optional[str] = None
        self.update_time: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UserShiftGroupsListBuilder":
        return UserShiftGroupsListBuilder()


class UserShiftGroupsListBuilder(object):
    def __init__(self) -> None:
        self._user_shift_groups_list = UserShiftGroupsList()

    def shift_group_id(self, shift_group_id: str) -> "UserShiftGroupsListBuilder":
        self._user_shift_groups_list.shift_group_id = shift_group_id
        return self

    def shift_group_name(self, shift_group_name: str) -> "UserShiftGroupsListBuilder":
        self._user_shift_groups_list.shift_group_name = shift_group_name
        return self

    def group_id(self, group_id: str) -> "UserShiftGroupsListBuilder":
        self._user_shift_groups_list.group_id = group_id
        return self

    def update_time(self, update_time: str) -> "UserShiftGroupsListBuilder":
        self._user_shift_groups_list.update_time = update_time
        return self

    def build(self) -> "UserShiftGroupsList":
        return self._user_shift_groups_list
