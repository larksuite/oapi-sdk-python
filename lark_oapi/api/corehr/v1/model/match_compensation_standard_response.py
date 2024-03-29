# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .match_compensation_standard_response_body import MatchCompensationStandardResponseBody


class MatchCompensationStandardResponse(BaseResponse):
    _types = {
        "data": MatchCompensationStandardResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[MatchCompensationStandardResponseBody] = None
        init(self, d, self._types)
