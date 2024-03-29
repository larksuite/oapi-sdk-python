# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .location import Location


class BatchGetLocationResponseBody(object):
    _types = {
        "items": List[Location],
    }

    def __init__(self, d=None):
        self.items: Optional[List[Location]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BatchGetLocationResponseBodyBuilder":
        return BatchGetLocationResponseBodyBuilder()


class BatchGetLocationResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._batch_get_location_response_body = BatchGetLocationResponseBody()

    def items(self, items: List[Location]) -> "BatchGetLocationResponseBodyBuilder":
        self._batch_get_location_response_body.items = items
        return self

    def build(self) -> "BatchGetLocationResponseBody":
        return self._batch_get_location_response_body
