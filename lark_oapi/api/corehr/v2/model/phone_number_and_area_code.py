# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .enum import Enum


class PhoneNumberAndAreaCode(object):
    _types = {
        "area_code": Enum,
        "phone_number": str,
    }

    def __init__(self, d=None):
        self.area_code: Optional[Enum] = None
        self.phone_number: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PhoneNumberAndAreaCodeBuilder":
        return PhoneNumberAndAreaCodeBuilder()


class PhoneNumberAndAreaCodeBuilder(object):
    def __init__(self) -> None:
        self._phone_number_and_area_code = PhoneNumberAndAreaCode()

    def area_code(self, area_code: Enum) -> "PhoneNumberAndAreaCodeBuilder":
        self._phone_number_and_area_code.area_code = area_code
        return self

    def phone_number(self, phone_number: str) -> "PhoneNumberAndAreaCodeBuilder":
        self._phone_number_and_area_code.phone_number = phone_number
        return self

    def build(self) -> "PhoneNumberAndAreaCode":
        return self._phone_number_and_area_code
