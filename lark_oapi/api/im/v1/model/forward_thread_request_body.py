# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class ForwardThreadRequestBody(object):
    _types = {
        "receive_id": str,
    }

    def __init__(self, d=None):
        self.receive_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ForwardThreadRequestBodyBuilder":
        return ForwardThreadRequestBodyBuilder()


class ForwardThreadRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._forward_thread_request_body = ForwardThreadRequestBody()

    def receive_id(self, receive_id: str) -> "ForwardThreadRequestBodyBuilder":
        self._forward_thread_request_body.receive_id = receive_id
        return self

    def build(self) -> "ForwardThreadRequestBody":
        return self._forward_thread_request_body
