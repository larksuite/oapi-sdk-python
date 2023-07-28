# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init


class InputSection(object):
    _types = {
        "name": str,
        "resource_type": str,
        "resource_id": str,
        "insert_before": str,
        "insert_after": str,
    }

    def __init__(self, d=None):
        self.name: Optional[str] = None
        self.resource_type: Optional[str] = None
        self.resource_id: Optional[str] = None
        self.insert_before: Optional[str] = None
        self.insert_after: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "InputSectionBuilder":
        return InputSectionBuilder()


class InputSectionBuilder(object):
    def __init__(self) -> None:
        self._input_section = InputSection()

    def name(self, name: str) -> "InputSectionBuilder":
        self._input_section.name = name
        return self

    def resource_type(self, resource_type: str) -> "InputSectionBuilder":
        self._input_section.resource_type = resource_type
        return self

    def resource_id(self, resource_id: str) -> "InputSectionBuilder":
        self._input_section.resource_id = resource_id
        return self

    def insert_before(self, insert_before: str) -> "InputSectionBuilder":
        self._input_section.insert_before = insert_before
        return self

    def insert_after(self, insert_after: str) -> "InputSectionBuilder":
        self._input_section.insert_after = insert_after
        return self

    def build(self) -> "InputSection":
        return self._input_section
