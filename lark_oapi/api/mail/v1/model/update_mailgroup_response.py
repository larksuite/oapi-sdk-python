# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .update_mailgroup_response_body import UpdateMailgroupResponseBody


class UpdateMailgroupResponse(BaseResponse):
    _types = {
        "data": UpdateMailgroupResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[UpdateMailgroupResponseBody] = None
        init(self, d, self._types)