# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.enum import HttpMethod, AccessTokenType
from lark_oapi.core.model import BaseRequest
from .update_chat_request_body import UpdateChatRequestBody


class UpdateChatRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.user_id_type: Optional[str] = None
        self.chat_id: Optional[str] = None
        self.request_body: Optional[UpdateChatRequestBody] = None

    @staticmethod
    def builder() -> "UpdateChatRequestBuilder":
        return UpdateChatRequestBuilder()


class UpdateChatRequestBuilder(object):

    def __init__(self) -> None:
        update_chat_request = UpdateChatRequest()
        update_chat_request.http_method = HttpMethod.PUT
        update_chat_request.uri = "/open-apis/im/v1/chats/:chat_id"
        update_chat_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._update_chat_request: UpdateChatRequest = update_chat_request

    def user_id_type(self, user_id_type: str) -> "UpdateChatRequestBuilder":
        self._update_chat_request.user_id_type = user_id_type
        self._update_chat_request.add_query("user_id_type", user_id_type)
        return self

    def chat_id(self, chat_id: str) -> "UpdateChatRequestBuilder":
        self._update_chat_request.chat_id = chat_id
        self._update_chat_request.paths["chat_id"] = str(chat_id)
        return self

    def request_body(self, request_body: UpdateChatRequestBody) -> "UpdateChatRequestBuilder":
        self._update_chat_request.request_body = request_body
        self._update_chat_request.body = request_body
        return self

    def build(self) -> UpdateChatRequest:
        return self._update_chat_request