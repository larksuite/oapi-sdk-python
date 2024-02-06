# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init


class FilterViewCondition(object):
    _types = {
        "condition_id": str,
        "filter_type": str,
        "compare_type": str,
        "expected": List[str],
    }

    def __init__(self, d=None):
        self.condition_id: Optional[str] = None
        self.filter_type: Optional[str] = None
        self.compare_type: Optional[str] = None
        self.expected: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FilterViewConditionBuilder":
        return FilterViewConditionBuilder()


class FilterViewConditionBuilder(object):
    def __init__(self) -> None:
        self._filter_view_condition = FilterViewCondition()

    def condition_id(self, condition_id: str) -> "FilterViewConditionBuilder":
        self._filter_view_condition.condition_id = condition_id
        return self

    def filter_type(self, filter_type: str) -> "FilterViewConditionBuilder":
        self._filter_view_condition.filter_type = filter_type
        return self

    def compare_type(self, compare_type: str) -> "FilterViewConditionBuilder":
        self._filter_view_condition.compare_type = compare_type
        return self

    def expected(self, expected: List[str]) -> "FilterViewConditionBuilder":
        self._filter_view_condition.expected = expected
        return self

    def build(self) -> "FilterViewCondition":
        return self._filter_view_condition