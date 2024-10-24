# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .protect_search_agency_response_body import ProtectSearchAgencyResponseBody


class ProtectSearchAgencyResponse(BaseResponse):
    _types = {
        "data": ProtectSearchAgencyResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[ProtectSearchAgencyResponseBody] = None
        init(self, d, self._types)
