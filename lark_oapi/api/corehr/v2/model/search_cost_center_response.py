# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .search_cost_center_response_body import SearchCostCenterResponseBody


class SearchCostCenterResponse(BaseResponse):
    _types = {
        "data": SearchCostCenterResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[SearchCostCenterResponseBody] = None
        init(self, d, self._types)
