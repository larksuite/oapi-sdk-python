# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class FormFieldVariableStringValue(object):
    _types = {
        "value": str,
    }

    def __init__(self, d=None):
        self.value: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FormFieldVariableStringValueBuilder":
        return FormFieldVariableStringValueBuilder()


class FormFieldVariableStringValueBuilder(object):
    def __init__(self) -> None:
        self._form_field_variable_string_value = FormFieldVariableStringValue()

    def value(self, value: str) -> "FormFieldVariableStringValueBuilder":
        self._form_field_variable_string_value.value = value
        return self

    def build(self) -> "FormFieldVariableStringValue":
        return self._form_field_variable_string_value
