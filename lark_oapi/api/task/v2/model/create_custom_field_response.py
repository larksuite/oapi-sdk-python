# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .create_custom_field_response_body import CreateCustomFieldResponseBody


class CreateCustomFieldResponse(BaseResponse):
    _types = {
        "data": CreateCustomFieldResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[CreateCustomFieldResponseBody] = None
        init(self, d, self._types)
