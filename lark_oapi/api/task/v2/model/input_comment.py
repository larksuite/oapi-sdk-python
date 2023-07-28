# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init


class InputComment(object):
    _types = {
        "content": str,
        "reply_to_comment_id": str,
        "resource_type": str,
        "resource_id": str,
    }

    def __init__(self, d=None):
        self.content: Optional[str] = None
        self.reply_to_comment_id: Optional[str] = None
        self.resource_type: Optional[str] = None
        self.resource_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "InputCommentBuilder":
        return InputCommentBuilder()


class InputCommentBuilder(object):
    def __init__(self) -> None:
        self._input_comment = InputComment()

    def content(self, content: str) -> "InputCommentBuilder":
        self._input_comment.content = content
        return self

    def reply_to_comment_id(self, reply_to_comment_id: str) -> "InputCommentBuilder":
        self._input_comment.reply_to_comment_id = reply_to_comment_id
        return self

    def resource_type(self, resource_type: str) -> "InputCommentBuilder":
        self._input_comment.resource_type = resource_type
        return self

    def resource_id(self, resource_id: str) -> "InputCommentBuilder":
        self._input_comment.resource_id = resource_id
        return self

    def build(self) -> "InputComment":
        return self._input_comment
