# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class MyAiInstanceDetailExtra(object):
    _types = {
        "instance_id": str,
    }

    def __init__(self, d=None):
        self.instance_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MyAiInstanceDetailExtraBuilder":
        return MyAiInstanceDetailExtraBuilder()


class MyAiInstanceDetailExtraBuilder(object):
    def __init__(self) -> None:
        self._my_ai_instance_detail_extra = MyAiInstanceDetailExtra()

    def instance_id(self, instance_id: str) -> "MyAiInstanceDetailExtraBuilder":
        self._my_ai_instance_detail_extra.instance_id = instance_id
        return self

    def build(self) -> "MyAiInstanceDetailExtra":
        return self._my_ai_instance_detail_extra
