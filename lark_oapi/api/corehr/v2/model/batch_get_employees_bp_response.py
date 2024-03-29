# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .batch_get_employees_bp_response_body import BatchGetEmployeesBpResponseBody


class BatchGetEmployeesBpResponse(BaseResponse):
    _types = {
        "data": BatchGetEmployeesBpResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[BatchGetEmployeesBpResponseBody] = None
        init(self, d, self._types)
