# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .period_rule import PeriodRule


class ListPeriodRuleResponseBody(object):
    _types = {
        "period_rules": List[PeriodRule],
    }

    def __init__(self, d=None):
        self.period_rules: Optional[List[PeriodRule]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ListPeriodRuleResponseBodyBuilder":
        return ListPeriodRuleResponseBodyBuilder()


class ListPeriodRuleResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._list_period_rule_response_body = ListPeriodRuleResponseBody()

    def period_rules(self, period_rules: List[PeriodRule]) -> "ListPeriodRuleResponseBodyBuilder":
        self._list_period_rule_response_body.period_rules = period_rules
        return self

    def build(self) -> "ListPeriodRuleResponseBody":
        return self._list_period_rule_response_body
