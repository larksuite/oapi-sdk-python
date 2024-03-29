# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .recognize_food_produce_license_response_body import RecognizeFoodProduceLicenseResponseBody


class RecognizeFoodProduceLicenseResponse(BaseResponse):
    _types = {
        "data": RecognizeFoodProduceLicenseResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[RecognizeFoodProduceLicenseResponseBody] = None
        init(self, d, self._types)
