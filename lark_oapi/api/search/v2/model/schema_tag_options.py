# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class SchemaTagOptions(object):
    _types = {
        "name": str,
        "color": str,
        "text": str,
    }

    def __init__(self, d=None):
        self.name: Optional[str] = None
        self.color: Optional[str] = None
        self.text: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SchemaTagOptionsBuilder":
        return SchemaTagOptionsBuilder()


class SchemaTagOptionsBuilder(object):
    def __init__(self) -> None:
        self._schema_tag_options = SchemaTagOptions()

    def name(self, name: str) -> "SchemaTagOptionsBuilder":
        self._schema_tag_options.name = name
        return self

    def color(self, color: str) -> "SchemaTagOptionsBuilder":
        self._schema_tag_options.color = color
        return self

    def text(self, text: str) -> "SchemaTagOptionsBuilder":
        self._schema_tag_options.text = text
        return self

    def build(self) -> "SchemaTagOptions":
        return self._schema_tag_options