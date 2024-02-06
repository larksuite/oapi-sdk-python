# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .get_progress_record_response_body import GetProgressRecordResponseBody


class GetProgressRecordResponse(BaseResponse):
    _types = {
        "data": GetProgressRecordResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[GetProgressRecordResponseBody] = None
        init(self, d, self._types)