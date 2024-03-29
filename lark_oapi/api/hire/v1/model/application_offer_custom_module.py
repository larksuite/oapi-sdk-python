# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .application_offer_custom_value import ApplicationOfferCustomValue


class ApplicationOfferCustomModule(object):
    _types = {
        "i_d": str,
        "object_list": List[ApplicationOfferCustomValue],
    }

    def __init__(self, d=None):
        self.i_d: Optional[str] = None
        self.object_list: Optional[List[ApplicationOfferCustomValue]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ApplicationOfferCustomModuleBuilder":
        return ApplicationOfferCustomModuleBuilder()


class ApplicationOfferCustomModuleBuilder(object):
    def __init__(self) -> None:
        self._application_offer_custom_module = ApplicationOfferCustomModule()

    def i_d(self, i_d: str) -> "ApplicationOfferCustomModuleBuilder":
        self._application_offer_custom_module.i_d = i_d
        return self

    def object_list(self, object_list: List[ApplicationOfferCustomValue]) -> "ApplicationOfferCustomModuleBuilder":
        self._application_offer_custom_module.object_list = object_list
        return self

    def build(self) -> "ApplicationOfferCustomModule":
        return self._application_offer_custom_module
