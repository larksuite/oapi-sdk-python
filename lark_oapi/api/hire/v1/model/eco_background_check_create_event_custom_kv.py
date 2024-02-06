# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class EcoBackgroundCheckCreateEventCustomKv(object):
    _types = {
        "key": str,
        "value": str,
    }

    def __init__(self, d=None):
        self.key: Optional[str] = None
        self.value: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "EcoBackgroundCheckCreateEventCustomKvBuilder":
        return EcoBackgroundCheckCreateEventCustomKvBuilder()


class EcoBackgroundCheckCreateEventCustomKvBuilder(object):
    def __init__(self) -> None:
        self._eco_background_check_create_event_custom_kv = EcoBackgroundCheckCreateEventCustomKv()

    def key(self, key: str) -> "EcoBackgroundCheckCreateEventCustomKvBuilder":
        self._eco_background_check_create_event_custom_kv.key = key
        return self

    def value(self, value: str) -> "EcoBackgroundCheckCreateEventCustomKvBuilder":
        self._eco_background_check_create_event_custom_kv.value = value
        return self

    def build(self) -> "EcoBackgroundCheckCreateEventCustomKv":
        return self._eco_background_check_create_event_custom_kv