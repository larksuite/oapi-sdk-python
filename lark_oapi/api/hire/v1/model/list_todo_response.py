# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .list_todo_response_body import ListTodoResponseBody


class ListTodoResponse(BaseResponse):
    _types = {
        "data": ListTodoResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[ListTodoResponseBody] = None
        init(self, d, self._types)
