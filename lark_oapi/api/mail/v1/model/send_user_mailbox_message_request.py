# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .message import Message


class SendUserMailboxMessageRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_mailbox_id: Optional[str] = None
        self.request_body: Optional[Message] = None

    @staticmethod
    def builder() -> "SendUserMailboxMessageRequestBuilder":
        return SendUserMailboxMessageRequestBuilder()


class SendUserMailboxMessageRequestBuilder(object):

    def __init__(self) -> None:
        send_user_mailbox_message_request = SendUserMailboxMessageRequest()
        send_user_mailbox_message_request.http_method = HttpMethod.POST
        send_user_mailbox_message_request.uri = "/open-apis/mail/v1/user_mailboxes/:user_mailbox_id/messages/send"
        send_user_mailbox_message_request.token_types = {AccessTokenType.USER}
        self._send_user_mailbox_message_request: SendUserMailboxMessageRequest = send_user_mailbox_message_request

    def user_mailbox_id(self, user_mailbox_id: str) -> "SendUserMailboxMessageRequestBuilder":
        self._send_user_mailbox_message_request.user_mailbox_id = user_mailbox_id
        self._send_user_mailbox_message_request.paths["user_mailbox_id"] = str(user_mailbox_id)
        return self

    def request_body(self, request_body: Message) -> "SendUserMailboxMessageRequestBuilder":
        self._send_user_mailbox_message_request.request_body = request_body
        self._send_user_mailbox_message_request.body = request_body
        return self

    def build(self) -> SendUserMailboxMessageRequest:
        return self._send_user_mailbox_message_request