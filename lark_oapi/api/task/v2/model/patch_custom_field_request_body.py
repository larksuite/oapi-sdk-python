# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .input_custom_field import InputCustomField


class PatchCustomFieldRequestBody(object):
    _types = {
        "custom_field": InputCustomField,
        "update_fields": List[str],
    }

    def __init__(self, d=None):
        self.custom_field: Optional[InputCustomField] = None
        self.update_fields: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PatchCustomFieldRequestBodyBuilder":
        return PatchCustomFieldRequestBodyBuilder()


class PatchCustomFieldRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._patch_custom_field_request_body = PatchCustomFieldRequestBody()

    def custom_field(self, custom_field: InputCustomField) -> "PatchCustomFieldRequestBodyBuilder":
        self._patch_custom_field_request_body.custom_field = custom_field
        return self

    def update_fields(self, update_fields: List[str]) -> "PatchCustomFieldRequestBodyBuilder":
        self._patch_custom_field_request_body.update_fields = update_fields
        return self

    def build(self) -> "PatchCustomFieldRequestBody":
        return self._patch_custom_field_request_body
