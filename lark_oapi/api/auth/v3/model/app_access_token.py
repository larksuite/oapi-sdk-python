# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class AppAccessToken(object):
    _types = {
    }

    def __init__(self, d=None):
        init(self, d, self._types)

    @staticmethod
    def builder() -> "AppAccessTokenBuilder":
        return AppAccessTokenBuilder()


class AppAccessTokenBuilder(object):
    def __init__(self) -> None:
        self._app_access_token = AppAccessToken()

    def build(self) -> "AppAccessToken":
        return self._app_access_token
