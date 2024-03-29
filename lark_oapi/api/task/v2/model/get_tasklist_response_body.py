# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .tasklist import Tasklist


class GetTasklistResponseBody(object):
    _types = {
        "tasklist": Tasklist,
    }

    def __init__(self, d=None):
        self.tasklist: Optional[Tasklist] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "GetTasklistResponseBodyBuilder":
        return GetTasklistResponseBodyBuilder()


class GetTasklistResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._get_tasklist_response_body = GetTasklistResponseBody()

    def tasklist(self, tasklist: Tasklist) -> "GetTasklistResponseBodyBuilder":
        self._get_tasklist_response_body.tasklist = tasklist
        return self

    def build(self) -> "GetTasklistResponseBody":
        return self._get_tasklist_response_body
