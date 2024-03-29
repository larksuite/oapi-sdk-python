# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .batch_get_employees_job_data_response_body import BatchGetEmployeesJobDataResponseBody


class BatchGetEmployeesJobDataResponse(BaseResponse):
    _types = {
        "data": BatchGetEmployeesJobDataResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[BatchGetEmployeesJobDataResponseBody] = None
        init(self, d, self._types)
