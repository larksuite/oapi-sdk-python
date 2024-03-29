# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .schema_field_answer_option import SchemaFieldAnswerOption


class PatchSchemaProperty(object):
    _types = {
        "name": str,
        "desc": str,
        "answer_option": SchemaFieldAnswerOption,
    }

    def __init__(self, d=None):
        self.name: Optional[str] = None
        self.desc: Optional[str] = None
        self.answer_option: Optional[SchemaFieldAnswerOption] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PatchSchemaPropertyBuilder":
        return PatchSchemaPropertyBuilder()


class PatchSchemaPropertyBuilder(object):
    def __init__(self) -> None:
        self._patch_schema_property = PatchSchemaProperty()

    def name(self, name: str) -> "PatchSchemaPropertyBuilder":
        self._patch_schema_property.name = name
        return self

    def desc(self, desc: str) -> "PatchSchemaPropertyBuilder":
        self._patch_schema_property.desc = desc
        return self

    def answer_option(self, answer_option: SchemaFieldAnswerOption) -> "PatchSchemaPropertyBuilder":
        self._patch_schema_property.answer_option = answer_option
        return self

    def build(self) -> "PatchSchemaProperty":
        return self._patch_schema_property
