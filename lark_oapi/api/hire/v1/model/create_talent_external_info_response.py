# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .create_talent_external_info_response_body import CreateTalentExternalInfoResponseBody


class CreateTalentExternalInfoResponse(BaseResponse):
    _types = {
        "data": CreateTalentExternalInfoResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[CreateTalentExternalInfoResponseBody] = None
        init(self, d, self._types)
