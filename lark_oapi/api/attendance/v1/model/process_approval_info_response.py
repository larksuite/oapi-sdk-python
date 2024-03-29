# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .process_approval_info_response_body import ProcessApprovalInfoResponseBody


class ProcessApprovalInfoResponse(BaseResponse):
    _types = {
        "data": ProcessApprovalInfoResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[ProcessApprovalInfoResponseBody] = None
        init(self, d, self._types)
