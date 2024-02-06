# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .patch_employee_response_body import PatchEmployeeResponseBody


class PatchEmployeeResponse(BaseResponse):
    _types = {
        "data": PatchEmployeeResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[PatchEmployeeResponseBody] = None
        init(self, d, self._types)