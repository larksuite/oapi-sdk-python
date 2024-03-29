# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .search_basic_info_district_response_body import SearchBasicInfoDistrictResponseBody


class SearchBasicInfoDistrictResponse(BaseResponse):
    _types = {
        "data": SearchBasicInfoDistrictResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[SearchBasicInfoDistrictResponseBody] = None
        init(self, d, self._types)
