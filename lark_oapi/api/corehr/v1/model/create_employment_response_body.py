# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from .employment_create import EmploymentCreate


class CreateEmploymentResponseBody(object):
    _types = {
        "employment": EmploymentCreate,
    }

    def __init__(self, d):
        self.employment: Optional[EmploymentCreate] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateEmploymentResponseBodyBuilder":
        return CreateEmploymentResponseBodyBuilder()


class CreateEmploymentResponseBodyBuilder(object):
    def __init__(self, create_employment_response_body: CreateEmploymentResponseBody = CreateEmploymentResponseBody({})) -> None:
        self._create_employment_response_body: CreateEmploymentResponseBody = create_employment_response_body
    
    def employment(self, employment: EmploymentCreate) -> "CreateEmploymentResponseBodyBuilder":
        self._create_employment_response_body.employment = employment
        return self
    
    def build(self) -> "CreateEmploymentResponseBody":
        return self._create_employment_response_body