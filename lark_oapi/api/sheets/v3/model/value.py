# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .cell_value import CellValue


class Value(object):
    _types = {
        "range": str,
        "values": List[list],
    }

    def __init__(self, d=None):
        self.range: Optional[str] = None
        self.values: Optional[List[list]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ValueBuilder":
        return ValueBuilder()


class ValueBuilder(object):
    def __init__(self) -> None:
        self._value = Value()

    def range(self, range: str) -> "ValueBuilder":
        self._value.range = range
        return self

    def values(self, values: List[list]) -> "ValueBuilder":
        self._value.values = values
        return self

    def build(self) -> "Value":
        return self._value
