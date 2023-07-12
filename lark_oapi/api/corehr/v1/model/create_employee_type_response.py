# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .create_employee_type_response_body import CreateEmployeeTypeResponseBody


class CreateEmployeeTypeResponse(BaseResponse):
    _types = {
        "data": CreateEmployeeTypeResponseBody
    }

    def __init__(self, d):
        super().__init__(d)
        self.data: Optional[CreateEmployeeTypeResponseBody] = None
        init(self, d, self._types)