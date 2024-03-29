# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .upload_all_file_response_body import UploadAllFileResponseBody


class UploadAllFileResponse(BaseResponse):
    _types = {
        "data": UploadAllFileResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[UploadAllFileResponseBody] = None
        init(self, d, self._types)
