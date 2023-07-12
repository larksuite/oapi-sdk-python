# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init


class CreatePreHireResponseBody(object):
    _types = {
        "pre_hire_id": str,
    }

    def __init__(self, d):
        self.pre_hire_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreatePreHireResponseBodyBuilder":
        return CreatePreHireResponseBodyBuilder()


class CreatePreHireResponseBodyBuilder(object):
    def __init__(self, create_pre_hire_response_body: CreatePreHireResponseBody = CreatePreHireResponseBody({})) -> None:
        self._create_pre_hire_response_body: CreatePreHireResponseBody = create_pre_hire_response_body
    
    def pre_hire_id(self, pre_hire_id: str) -> "CreatePreHireResponseBodyBuilder":
        self._create_pre_hire_response_body.pre_hire_id = pre_hire_id
        return self
    
    def build(self) -> "CreatePreHireResponseBody":
        return self._create_pre_hire_response_body