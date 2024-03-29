# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class MyAiResponsePresent(object):
    _types = {
        "type": str,
        "body": str,
        "interactable": bool,
        "operation_type": str,
        "operation_url": str,
        "callback_url": str,
        "callback_info": str,
    }

    def __init__(self, d=None):
        self.type: Optional[str] = None
        self.body: Optional[str] = None
        self.interactable: Optional[bool] = None
        self.operation_type: Optional[str] = None
        self.operation_url: Optional[str] = None
        self.callback_url: Optional[str] = None
        self.callback_info: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MyAiResponsePresentBuilder":
        return MyAiResponsePresentBuilder()


class MyAiResponsePresentBuilder(object):
    def __init__(self) -> None:
        self._my_ai_response_present = MyAiResponsePresent()

    def type(self, type: str) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.type = type
        return self

    def body(self, body: str) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.body = body
        return self

    def interactable(self, interactable: bool) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.interactable = interactable
        return self

    def operation_type(self, operation_type: str) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.operation_type = operation_type
        return self

    def operation_url(self, operation_url: str) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.operation_url = operation_url
        return self

    def callback_url(self, callback_url: str) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.callback_url = callback_url
        return self

    def callback_info(self, callback_info: str) -> "MyAiResponsePresentBuilder":
        self._my_ai_response_present.callback_info = callback_info
        return self

    def build(self) -> "MyAiResponsePresent":
        return self._my_ai_response_present
