# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .rule import Rule


class GetRuleExternalResponseBody(object):
    _types = {
        "rules": List[Rule],
    }

    def __init__(self, d=None):
        self.rules: Optional[List[Rule]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "GetRuleExternalResponseBodyBuilder":
        return GetRuleExternalResponseBodyBuilder()


class GetRuleExternalResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._get_rule_external_response_body = GetRuleExternalResponseBody()

    def rules(self, rules: List[Rule]) -> "GetRuleExternalResponseBodyBuilder":
        self._get_rule_external_response_body.rules = rules
        return self

    def build(self) -> "GetRuleExternalResponseBody":
        return self._get_rule_external_response_body
