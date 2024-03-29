# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class DocLink(object):
    _types = {
        "title": str,
        "url": str,
    }

    def __init__(self, d=None):
        self.title: Optional[str] = None
        self.url: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DocLinkBuilder":
        return DocLinkBuilder()


class DocLinkBuilder(object):
    def __init__(self) -> None:
        self._doc_link = DocLink()

    def title(self, title: str) -> "DocLinkBuilder":
        self._doc_link.title = title
        return self

    def url(self, url: str) -> "DocLinkBuilder":
        self._doc_link.url = url
        return self

    def build(self) -> "DocLink":
        return self._doc_link
