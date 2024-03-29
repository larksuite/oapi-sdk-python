# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .recognize_food_manage_license_response_body import RecognizeFoodManageLicenseResponseBody


class RecognizeFoodManageLicenseResponse(BaseResponse):
    _types = {
        "data": RecognizeFoodManageLicenseResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[RecognizeFoodManageLicenseResponseBody] = None
        init(self, d, self._types)
