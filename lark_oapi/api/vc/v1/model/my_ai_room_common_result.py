# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .my_ai_room_openapi_response import MyAiRoomOpenapiResponse


class MyAiRoomCommonResult(object):
    _types = {
        "room_reply": str,
        "openapi_response": MyAiRoomOpenapiResponse,
    }

    def __init__(self, d=None):
        self.room_reply: Optional[str] = None
        self.openapi_response: Optional[MyAiRoomOpenapiResponse] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MyAiRoomCommonResultBuilder":
        return MyAiRoomCommonResultBuilder()


class MyAiRoomCommonResultBuilder(object):
    def __init__(self) -> None:
        self._my_ai_room_common_result = MyAiRoomCommonResult()

    def room_reply(self, room_reply: str) -> "MyAiRoomCommonResultBuilder":
        self._my_ai_room_common_result.room_reply = room_reply
        return self

    def openapi_response(self, openapi_response: MyAiRoomOpenapiResponse) -> "MyAiRoomCommonResultBuilder":
        self._my_ai_room_common_result.openapi_response = openapi_response
        return self

    def build(self) -> "MyAiRoomCommonResult":
        return self._my_ai_room_common_result