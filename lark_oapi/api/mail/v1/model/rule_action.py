# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .rule_action_item import RuleActionItem


class RuleAction(object):
    _types = {
        "items": List[RuleActionItem],
    }

    def __init__(self, d=None):
        self.items: Optional[List[RuleActionItem]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RuleActionBuilder":
        return RuleActionBuilder()


class RuleActionBuilder(object):
    def __init__(self) -> None:
        self._rule_action = RuleAction()

    def items(self, items: List[RuleActionItem]) -> "RuleActionBuilder":
        self._rule_action.items = items
        return self

    def build(self) -> "RuleAction":
        return self._rule_action
