# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .classification_filter import ClassificationFilter


class SearchEntityRequestBody(object):
    _types = {
        "query": str,
        "classification_filter": ClassificationFilter,
        "sources": List[int],
        "creators": List[str],
    }

    def __init__(self, d=None):
        self.query: Optional[str] = None
        self.classification_filter: Optional[ClassificationFilter] = None
        self.sources: Optional[List[int]] = None
        self.creators: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchEntityRequestBodyBuilder":
        return SearchEntityRequestBodyBuilder()


class SearchEntityRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._search_entity_request_body = SearchEntityRequestBody()

    def query(self, query: str) -> "SearchEntityRequestBodyBuilder":
        self._search_entity_request_body.query = query
        return self

    def classification_filter(self, classification_filter: ClassificationFilter) -> "SearchEntityRequestBodyBuilder":
        self._search_entity_request_body.classification_filter = classification_filter
        return self

    def sources(self, sources: List[int]) -> "SearchEntityRequestBodyBuilder":
        self._search_entity_request_body.sources = sources
        return self

    def creators(self, creators: List[str]) -> "SearchEntityRequestBodyBuilder":
        self._search_entity_request_body.creators = creators
        return self

    def build(self) -> "SearchEntityRequestBody":
        return self._search_entity_request_body