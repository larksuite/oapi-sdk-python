# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .i18n_v2 import I18nV2


class CustomOrgList(object):
    _types = {
        "custom_org_name": I18nV2,
        "custom_org_id": str,
        "rate": str,
    }

    def __init__(self, d=None):
        self.custom_org_name: Optional[I18nV2] = None
        self.custom_org_id: Optional[str] = None
        self.rate: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CustomOrgListBuilder":
        return CustomOrgListBuilder()


class CustomOrgListBuilder(object):
    def __init__(self) -> None:
        self._custom_org_list = CustomOrgList()

    def custom_org_name(self, custom_org_name: I18nV2) -> "CustomOrgListBuilder":
        self._custom_org_list.custom_org_name = custom_org_name
        return self

    def custom_org_id(self, custom_org_id: str) -> "CustomOrgListBuilder":
        self._custom_org_list.custom_org_id = custom_org_id
        return self

    def rate(self, rate: str) -> "CustomOrgListBuilder":
        self._custom_org_list.rate = rate
        return self

    def build(self) -> "CustomOrgList":
        return self._custom_org_list