# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class UpdateApplicationManagementRequestBody(object):
    _types = {
        "enable": bool,
    }

    def __init__(self, d=None):
        self.enable: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UpdateApplicationManagementRequestBodyBuilder":
        return UpdateApplicationManagementRequestBodyBuilder()


class UpdateApplicationManagementRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._update_application_management_request_body = UpdateApplicationManagementRequestBody()

    def enable(self, enable: bool) -> "UpdateApplicationManagementRequestBodyBuilder":
        self._update_application_management_request_body.enable = enable
        return self

    def build(self) -> "UpdateApplicationManagementRequestBody":
        return self._update_application_management_request_body
