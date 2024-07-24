# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .website_job_post import WebsiteJobPost


class SearchJobPublishRecordResponseBody(object):
    _types = {
        "items": List[WebsiteJobPost],
        "has_more": bool,
        "page_token": str,
    }

    def __init__(self, d=None):
        self.items: Optional[List[WebsiteJobPost]] = None
        self.has_more: Optional[bool] = None
        self.page_token: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchJobPublishRecordResponseBodyBuilder":
        return SearchJobPublishRecordResponseBodyBuilder()


class SearchJobPublishRecordResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._search_job_publish_record_response_body = SearchJobPublishRecordResponseBody()

    def items(self, items: List[WebsiteJobPost]) -> "SearchJobPublishRecordResponseBodyBuilder":
        self._search_job_publish_record_response_body.items = items
        return self

    def has_more(self, has_more: bool) -> "SearchJobPublishRecordResponseBodyBuilder":
        self._search_job_publish_record_response_body.has_more = has_more
        return self

    def page_token(self, page_token: str) -> "SearchJobPublishRecordResponseBodyBuilder":
        self._search_job_publish_record_response_body.page_token = page_token
        return self

    def build(self) -> "SearchJobPublishRecordResponseBody":
        return self._search_job_publish_record_response_body
