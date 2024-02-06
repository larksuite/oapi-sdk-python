# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class BaseBilingualWithId(object):
    _types = {
        "id": str,
        "zh_name": str,
        "en_name": str,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.zh_name: Optional[str] = None
        self.en_name: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BaseBilingualWithIdBuilder":
        return BaseBilingualWithIdBuilder()


class BaseBilingualWithIdBuilder(object):
    def __init__(self) -> None:
        self._base_bilingual_with_id = BaseBilingualWithId()

    def id(self, id: str) -> "BaseBilingualWithIdBuilder":
        self._base_bilingual_with_id.id = id
        return self

    def zh_name(self, zh_name: str) -> "BaseBilingualWithIdBuilder":
        self._base_bilingual_with_id.zh_name = zh_name
        return self

    def en_name(self, en_name: str) -> "BaseBilingualWithIdBuilder":
        self._base_bilingual_with_id.en_name = en_name
        return self

    def build(self) -> "BaseBilingualWithId":
        return self._base_bilingual_with_id