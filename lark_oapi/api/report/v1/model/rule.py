# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .form_field import FormField


class Rule(object):
    _types = {
        "rule_id": int,
        "name": str,
        "icon_name": str,
        "created_at": int,
        "creator_user_id": str,
        "creator_user_name": str,
        "owner_user_id": str,
        "owner_user_name": str,
        "form_schema": List[FormField],
        "is_deleted": int,
        "need_report_user_ids": List[str],
        "need_report_department_ids": List[str],
        "need_report_chat_ids": List[str],
        "cc_user_ids": List[str],
        "cc_department_ids": List[str],
        "to_user_ids": List[str],
        "to_chat_ids": List[str],
        "to_leaders": List[int],
        "to_department_owners": List[int],
        "manager_user_ids": List[str],
        "cc_chat_ids": List[str],
    }

    def __init__(self, d=None):
        self.rule_id: Optional[int] = None
        self.name: Optional[str] = None
        self.icon_name: Optional[str] = None
        self.created_at: Optional[int] = None
        self.creator_user_id: Optional[str] = None
        self.creator_user_name: Optional[str] = None
        self.owner_user_id: Optional[str] = None
        self.owner_user_name: Optional[str] = None
        self.form_schema: Optional[List[FormField]] = None
        self.is_deleted: Optional[int] = None
        self.need_report_user_ids: Optional[List[str]] = None
        self.need_report_department_ids: Optional[List[str]] = None
        self.need_report_chat_ids: Optional[List[str]] = None
        self.cc_user_ids: Optional[List[str]] = None
        self.cc_department_ids: Optional[List[str]] = None
        self.to_user_ids: Optional[List[str]] = None
        self.to_chat_ids: Optional[List[str]] = None
        self.to_leaders: Optional[List[int]] = None
        self.to_department_owners: Optional[List[int]] = None
        self.manager_user_ids: Optional[List[str]] = None
        self.cc_chat_ids: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RuleBuilder":
        return RuleBuilder()


class RuleBuilder(object):
    def __init__(self) -> None:
        self._rule = Rule()

    def rule_id(self, rule_id: int) -> "RuleBuilder":
        self._rule.rule_id = rule_id
        return self

    def name(self, name: str) -> "RuleBuilder":
        self._rule.name = name
        return self

    def icon_name(self, icon_name: str) -> "RuleBuilder":
        self._rule.icon_name = icon_name
        return self

    def created_at(self, created_at: int) -> "RuleBuilder":
        self._rule.created_at = created_at
        return self

    def creator_user_id(self, creator_user_id: str) -> "RuleBuilder":
        self._rule.creator_user_id = creator_user_id
        return self

    def creator_user_name(self, creator_user_name: str) -> "RuleBuilder":
        self._rule.creator_user_name = creator_user_name
        return self

    def owner_user_id(self, owner_user_id: str) -> "RuleBuilder":
        self._rule.owner_user_id = owner_user_id
        return self

    def owner_user_name(self, owner_user_name: str) -> "RuleBuilder":
        self._rule.owner_user_name = owner_user_name
        return self

    def form_schema(self, form_schema: List[FormField]) -> "RuleBuilder":
        self._rule.form_schema = form_schema
        return self

    def is_deleted(self, is_deleted: int) -> "RuleBuilder":
        self._rule.is_deleted = is_deleted
        return self

    def need_report_user_ids(self, need_report_user_ids: List[str]) -> "RuleBuilder":
        self._rule.need_report_user_ids = need_report_user_ids
        return self

    def need_report_department_ids(self, need_report_department_ids: List[str]) -> "RuleBuilder":
        self._rule.need_report_department_ids = need_report_department_ids
        return self

    def need_report_chat_ids(self, need_report_chat_ids: List[str]) -> "RuleBuilder":
        self._rule.need_report_chat_ids = need_report_chat_ids
        return self

    def cc_user_ids(self, cc_user_ids: List[str]) -> "RuleBuilder":
        self._rule.cc_user_ids = cc_user_ids
        return self

    def cc_department_ids(self, cc_department_ids: List[str]) -> "RuleBuilder":
        self._rule.cc_department_ids = cc_department_ids
        return self

    def to_user_ids(self, to_user_ids: List[str]) -> "RuleBuilder":
        self._rule.to_user_ids = to_user_ids
        return self

    def to_chat_ids(self, to_chat_ids: List[str]) -> "RuleBuilder":
        self._rule.to_chat_ids = to_chat_ids
        return self

    def to_leaders(self, to_leaders: List[int]) -> "RuleBuilder":
        self._rule.to_leaders = to_leaders
        return self

    def to_department_owners(self, to_department_owners: List[int]) -> "RuleBuilder":
        self._rule.to_department_owners = to_department_owners
        return self

    def manager_user_ids(self, manager_user_ids: List[str]) -> "RuleBuilder":
        self._rule.manager_user_ids = manager_user_ids
        return self

    def cc_chat_ids(self, cc_chat_ids: List[str]) -> "RuleBuilder":
        self._rule.cc_chat_ids = cc_chat_ids
        return self

    def build(self) -> "Rule":
        return self._rule
