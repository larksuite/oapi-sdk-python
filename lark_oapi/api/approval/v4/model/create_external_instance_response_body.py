# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from .external_instance import ExternalInstance


class CreateExternalInstanceResponseBody(object):
    _types = {
        "data": ExternalInstance,
    }

    def __init__(self, d):
        self.data: Optional[ExternalInstance] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateExternalInstanceResponseBodyBuilder":
        return CreateExternalInstanceResponseBodyBuilder()


class CreateExternalInstanceResponseBodyBuilder(object):
    def __init__(self, create_external_instance_response_body: CreateExternalInstanceResponseBody = CreateExternalInstanceResponseBody({})) -> None:
        self._create_external_instance_response_body: CreateExternalInstanceResponseBody = create_external_instance_response_body
    
    def data(self, data: ExternalInstance) -> "CreateExternalInstanceResponseBodyBuilder":
        self._create_external_instance_response_body.data = data
        return self
    
    def build(self) -> "CreateExternalInstanceResponseBody":
        return self._create_external_instance_response_body