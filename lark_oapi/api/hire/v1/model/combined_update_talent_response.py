# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .combined_update_talent_response_body import CombinedUpdateTalentResponseBody


class CombinedUpdateTalentResponse(BaseResponse):
    _types = {
        "data": CombinedUpdateTalentResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[CombinedUpdateTalentResponseBody] = None
        init(self, d, self._types)
