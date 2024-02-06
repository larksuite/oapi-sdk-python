# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .comment import Comment


class ListCommentResponseBody(object):
    _types = {
        "items": List[Comment],
        "page_token": str,
        "has_more": bool,
    }

    def __init__(self, d=None):
        self.items: Optional[List[Comment]] = None
        self.page_token: Optional[str] = None
        self.has_more: Optional[bool] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ListCommentResponseBodyBuilder":
        return ListCommentResponseBodyBuilder()


class ListCommentResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._list_comment_response_body = ListCommentResponseBody()

    def items(self, items: List[Comment]) -> "ListCommentResponseBodyBuilder":
        self._list_comment_response_body.items = items
        return self

    def page_token(self, page_token: str) -> "ListCommentResponseBodyBuilder":
        self._list_comment_response_body.page_token = page_token
        return self

    def has_more(self, has_more: bool) -> "ListCommentResponseBodyBuilder":
        self._list_comment_response_body.has_more = has_more
        return self

    def build(self) -> "ListCommentResponseBody":
        return self._list_comment_response_body