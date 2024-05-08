from typing import Dict, Optional, Any

from lark_oapi.core.construct import init
from lark_oapi.core.model import RawRequest


class EventOperator(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.tenant_key: Optional[str] = None
        self.user_id: Optional[str] = None
        self.open_id: Optional[str] = None
        init(self, d, self._types)


class EventAction(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.value: Dict[str, Any] = {}
        self.form_value: Dict[str, Any] = {}
        self.timezone: Optional[str] = None
        self.name: Optional[str] = None
        self.tag: Optional[str] = None
        self.option: Dict[str, Any] = {}
        init(self, d, self._types)


class EventContext(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.url: Optional[str] = None
        self.preview_token: Optional[str] = None
        self.open_message_id: Optional[str] = None
        self.open_chat_id: Optional[str] = None
        init(self, d, self._types)


class Header(object):
    _types = {}

    def __init__(self, d=None) -> None:
        self.event_id: Optional[str] = None
        self.token: Optional[str] = None
        self.create_time: Optional[str] = None
        self.event_type: Optional[str] = None
        self.tenant_key: Optional[str] = None
        self.app_id: Optional[str] = None
        init(self, d, self._types)
        

class Event(object):
    _types = {
        "operator": EventOperator,
        "action": EventAction,
        "context": EventContext
    }

    def __init__(self, d=None) -> None:
        self.operator: Optional[EventOperator] = None
        self.token: Optional[str] = None
        self.action: Optional[EventAction] = None
        self.host: Optional[str] = None
        self.delivery_type: Optional[str] = None
        self.context: Optional[EventContext] = None
        init(self, d, self._types)


class Card(object):
    _types = {
        "header": Header,
        "event": Event
    }

    def __init__(self, d=None) -> None:
        self.schema: Optional[str] = None
        self.header: Optional[Header] = None
        self.event: Optional[Event] = None
        self.token: Optional[str] = None
        self.challenge: Optional[str] = None
        self.type: Optional[str] = None
        self.raw: Optional[RawRequest] = None
        init(self, d, self._types)
