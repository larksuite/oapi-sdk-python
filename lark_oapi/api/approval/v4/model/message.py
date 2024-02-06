# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class Message(object):
    _types = {
        "id": str,
        "receive_id": str,
        "content": str,
        "msg_type": str,
        "config": str,
        "extra": str,
        "uuid": str,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.receive_id: Optional[str] = None
        self.content: Optional[str] = None
        self.msg_type: Optional[str] = None
        self.config: Optional[str] = None
        self.extra: Optional[str] = None
        self.uuid: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "MessageBuilder":
        return MessageBuilder()


class MessageBuilder(object):
    def __init__(self) -> None:
        self._message = Message()

    def id(self, id: str) -> "MessageBuilder":
        self._message.id = id
        return self

    def receive_id(self, receive_id: str) -> "MessageBuilder":
        self._message.receive_id = receive_id
        return self

    def content(self, content: str) -> "MessageBuilder":
        self._message.content = content
        return self

    def msg_type(self, msg_type: str) -> "MessageBuilder":
        self._message.msg_type = msg_type
        return self

    def config(self, config: str) -> "MessageBuilder":
        self._message.config = config
        return self

    def extra(self, extra: str) -> "MessageBuilder":
        self._message.extra = extra
        return self

    def uuid(self, uuid: str) -> "MessageBuilder":
        self._message.uuid = uuid
        return self

    def build(self) -> "Message":
        return self._message