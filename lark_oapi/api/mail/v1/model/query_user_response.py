# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .query_user_response_body import QueryUserResponseBody


class QueryUserResponse(BaseResponse):
    _types = {
        "data": QueryUserResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[QueryUserResponseBody] = None
        init(self, d, self._types)