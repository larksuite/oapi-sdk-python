# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class ItemContent(object):
    _types = {
        "format": str,
        "content_data": str,
    }

    def __init__(self, d=None):
        self.format: Optional[str] = None
        self.content_data: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ItemContentBuilder":
        return ItemContentBuilder()


class ItemContentBuilder(object):
    def __init__(self) -> None:
        self._item_content = ItemContent()

    def format(self, format: str) -> "ItemContentBuilder":
        self._item_content.format = format
        return self

    def content_data(self, content_data: str) -> "ItemContentBuilder":
        self._item_content.content_data = content_data
        return self

    def build(self) -> "ItemContent":
        return self._item_content