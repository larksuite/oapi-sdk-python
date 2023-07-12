# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .query_transfer_type_response_body import QueryTransferTypeResponseBody


class QueryTransferTypeResponse(BaseResponse):
    _types = {
        "data": QueryTransferTypeResponseBody
    }

    def __init__(self, d):
        super().__init__(d)
        self.data: Optional[QueryTransferTypeResponseBody] = None
        init(self, d, self._types)