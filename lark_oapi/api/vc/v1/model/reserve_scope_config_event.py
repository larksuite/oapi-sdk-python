# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .subscribe_department import SubscribeDepartment
from .subscribe_user_event import SubscribeUserEvent


class ReserveScopeConfigEvent(object):
    _types = {
        "allow_all_users": int,
        "allow_users": List[SubscribeUserEvent],
        "allow_depts": List[SubscribeDepartment],
    }

    def __init__(self, d=None):
        self.allow_all_users: Optional[int] = None
        self.allow_users: Optional[List[SubscribeUserEvent]] = None
        self.allow_depts: Optional[List[SubscribeDepartment]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ReserveScopeConfigEventBuilder":
        return ReserveScopeConfigEventBuilder()


class ReserveScopeConfigEventBuilder(object):
    def __init__(self) -> None:
        self._reserve_scope_config_event = ReserveScopeConfigEvent()

    def allow_all_users(self, allow_all_users: int) -> "ReserveScopeConfigEventBuilder":
        self._reserve_scope_config_event.allow_all_users = allow_all_users
        return self

    def allow_users(self, allow_users: List[SubscribeUserEvent]) -> "ReserveScopeConfigEventBuilder":
        self._reserve_scope_config_event.allow_users = allow_users
        return self

    def allow_depts(self, allow_depts: List[SubscribeDepartment]) -> "ReserveScopeConfigEventBuilder":
        self._reserve_scope_config_event.allow_depts = allow_depts
        return self

    def build(self) -> "ReserveScopeConfigEvent":
        return self._reserve_scope_config_event