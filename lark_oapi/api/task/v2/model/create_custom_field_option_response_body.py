# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .option import Option


class CreateCustomFieldOptionResponseBody(object):
    _types = {
        "option": Option,
    }

    def __init__(self, d=None):
        self.option: Optional[Option] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateCustomFieldOptionResponseBodyBuilder":
        return CreateCustomFieldOptionResponseBodyBuilder()


class CreateCustomFieldOptionResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_custom_field_option_response_body = CreateCustomFieldOptionResponseBody()

    def option(self, option: Option) -> "CreateCustomFieldOptionResponseBodyBuilder":
        self._create_custom_field_option_response_body.option = option
        return self

    def build(self) -> "CreateCustomFieldOptionResponseBody":
        return self._create_custom_field_option_response_body
