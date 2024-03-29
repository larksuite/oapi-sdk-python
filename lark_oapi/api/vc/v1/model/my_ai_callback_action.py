# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .my_ai_callback_action_value import MyAiCallbackActionValue


class MyAiCallbackAction(object):
    _types = {
        "value": MyAiCallbackActionValue,
        "tag": str,
    }

    def __init__(self, d=None):
        self.value: Optional[MyAiCallbackActionValue] = None
        self.tag: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MyAiCallbackActionBuilder":
        return MyAiCallbackActionBuilder()


class MyAiCallbackActionBuilder(object):
    def __init__(self) -> None:
        self._my_ai_callback_action = MyAiCallbackAction()

    def value(self, value: MyAiCallbackActionValue) -> "MyAiCallbackActionBuilder":
        self._my_ai_callback_action.value = value
        return self

    def tag(self, tag: str) -> "MyAiCallbackActionBuilder":
        self._my_ai_callback_action.tag = tag
        return self

    def build(self) -> "MyAiCallbackAction":
        return self._my_ai_callback_action
