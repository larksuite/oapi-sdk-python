# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .rule_detail import RuleDetail


class Grant(object):
    _types = {
        "id": str,
        "badge_id": str,
        "name": str,
        "grant_type": int,
        "time_zone": str,
        "rule_detail": RuleDetail,
        "is_grant_all": bool,
        "user_ids": List[str],
        "department_ids": List[str],
        "group_ids": List[str],
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.badge_id: Optional[str] = None
        self.name: Optional[str] = None
        self.grant_type: Optional[int] = None
        self.time_zone: Optional[str] = None
        self.rule_detail: Optional[RuleDetail] = None
        self.is_grant_all: Optional[bool] = None
        self.user_ids: Optional[List[str]] = None
        self.department_ids: Optional[List[str]] = None
        self.group_ids: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "GrantBuilder":
        return GrantBuilder()


class GrantBuilder(object):
    def __init__(self) -> None:
        self._grant = Grant()

    def id(self, id: str) -> "GrantBuilder":
        self._grant.id = id
        return self

    def badge_id(self, badge_id: str) -> "GrantBuilder":
        self._grant.badge_id = badge_id
        return self

    def name(self, name: str) -> "GrantBuilder":
        self._grant.name = name
        return self

    def grant_type(self, grant_type: int) -> "GrantBuilder":
        self._grant.grant_type = grant_type
        return self

    def time_zone(self, time_zone: str) -> "GrantBuilder":
        self._grant.time_zone = time_zone
        return self

    def rule_detail(self, rule_detail: RuleDetail) -> "GrantBuilder":
        self._grant.rule_detail = rule_detail
        return self

    def is_grant_all(self, is_grant_all: bool) -> "GrantBuilder":
        self._grant.is_grant_all = is_grant_all
        return self

    def user_ids(self, user_ids: List[str]) -> "GrantBuilder":
        self._grant.user_ids = user_ids
        return self

    def department_ids(self, department_ids: List[str]) -> "GrantBuilder":
        self._grant.department_ids = department_ids
        return self

    def group_ids(self, group_ids: List[str]) -> "GrantBuilder":
        self._grant.group_ids = group_ids
        return self

    def build(self) -> "Grant":
        return self._grant