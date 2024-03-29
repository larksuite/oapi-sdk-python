# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class TrainEntity(object):
    _types = {
        "type": str,
        "value": str,
    }

    def __init__(self, d=None):
        self.type: Optional[str] = None
        self.value: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "TrainEntityBuilder":
        return TrainEntityBuilder()


class TrainEntityBuilder(object):
    def __init__(self) -> None:
        self._train_entity = TrainEntity()

    def type(self, type: str) -> "TrainEntityBuilder":
        self._train_entity.type = type
        return self

    def value(self, value: str) -> "TrainEntityBuilder":
        self._train_entity.value = value
        return self

    def build(self) -> "TrainEntity":
        return self._train_entity
