# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .chat_top_notice import ChatTopNotice


class PutTopNoticeChatTopNoticeRequestBody(object):
    _types = {
        "chat_top_notice": List[ChatTopNotice],
    }

    def __init__(self, d=None):
        self.chat_top_notice: Optional[List[ChatTopNotice]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PutTopNoticeChatTopNoticeRequestBodyBuilder":
        return PutTopNoticeChatTopNoticeRequestBodyBuilder()


class PutTopNoticeChatTopNoticeRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._put_top_notice_chat_top_notice_request_body = PutTopNoticeChatTopNoticeRequestBody()

    def chat_top_notice(self, chat_top_notice: List[ChatTopNotice]) -> "PutTopNoticeChatTopNoticeRequestBodyBuilder":
        self._put_top_notice_chat_top_notice_request_body.chat_top_notice = chat_top_notice
        return self

    def build(self) -> "PutTopNoticeChatTopNoticeRequestBody":
        return self._put_top_notice_chat_top_notice_request_body