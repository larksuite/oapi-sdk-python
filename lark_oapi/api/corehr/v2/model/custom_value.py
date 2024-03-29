# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class CustomValue(object):
    _types = {
        "value_boolean": bool,
        "value_enum_id": str,
    }

    def __init__(self, d=None):
        self.value_boolean: Optional[bool] = None
        self.value_enum_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CustomValueBuilder":
        return CustomValueBuilder()


class CustomValueBuilder(object):
    def __init__(self) -> None:
        self._custom_value = CustomValue()

    def value_boolean(self, value_boolean: bool) -> "CustomValueBuilder":
        self._custom_value.value_boolean = value_boolean
        return self

    def value_enum_id(self, value_enum_id: str) -> "CustomValueBuilder":
        self._custom_value.value_enum_id = value_enum_id
        return self

    def build(self) -> "CustomValue":
        return self._custom_value
