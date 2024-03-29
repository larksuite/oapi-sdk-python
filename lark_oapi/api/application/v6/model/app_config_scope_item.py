# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class AppConfigScopeItem(object):
    _types = {
        "scope_name": str,
        "token_type": str,
    }

    def __init__(self, d=None):
        self.scope_name: Optional[str] = None
        self.token_type: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AppConfigScopeItemBuilder":
        return AppConfigScopeItemBuilder()


class AppConfigScopeItemBuilder(object):
    def __init__(self) -> None:
        self._app_config_scope_item = AppConfigScopeItem()

    def scope_name(self, scope_name: str) -> "AppConfigScopeItemBuilder":
        self._app_config_scope_item.scope_name = scope_name
        return self

    def token_type(self, token_type: str) -> "AppConfigScopeItemBuilder":
        self._app_config_scope_item.token_type = token_type
        return self

    def build(self) -> "AppConfigScopeItem":
        return self._app_config_scope_item
