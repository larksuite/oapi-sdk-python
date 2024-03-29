# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .search_basic_info_bank_response_body import SearchBasicInfoBankResponseBody


class SearchBasicInfoBankResponse(BaseResponse):
    _types = {
        "data": SearchBasicInfoBankResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[SearchBasicInfoBankResponseBody] = None
        init(self, d, self._types)
