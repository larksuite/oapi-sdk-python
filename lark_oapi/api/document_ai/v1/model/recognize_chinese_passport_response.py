# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .recognize_chinese_passport_response_body import RecognizeChinesePassportResponseBody


class RecognizeChinesePassportResponse(BaseResponse):
    _types = {
        "data": RecognizeChinesePassportResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[RecognizeChinesePassportResponseBody] = None
        init(self, d, self._types)
