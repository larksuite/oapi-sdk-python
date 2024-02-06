# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .comment import Comment


class GetTaskCommentResponseBody(object):
    _types = {
        "comment": Comment,
    }

    def __init__(self, d=None):
        self.comment: Optional[Comment] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "GetTaskCommentResponseBodyBuilder":
        return GetTaskCommentResponseBodyBuilder()


class GetTaskCommentResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._get_task_comment_response_body = GetTaskCommentResponseBody()

    def comment(self, comment: Comment) -> "GetTaskCommentResponseBodyBuilder":
        self._get_task_comment_response_body.comment = comment
        return self

    def build(self) -> "GetTaskCommentResponseBody":
        return self._get_task_comment_response_body