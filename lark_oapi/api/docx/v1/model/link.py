# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init


class Link(object):
    _types = {
        "url": str,
    }

    def __init__(self, d):
        self.url: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "LinkBuilder":
        return LinkBuilder()


class LinkBuilder(object):
    def __init__(self, link: Link = Link({})) -> None:
        self._link: Link = link
    
    def url(self, url: str) -> "LinkBuilder":
        self._link.url = url
        return self
    
    def build(self) -> "Link":
        return self._link