# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .customized_field_display_item import CustomizedFieldDisplayItem
from .ticket_user_event import TicketUserEvent


class P2HelpdeskTicketCreatedV1Data(object):
    _types = {
        "ticket_id": str,
        "helpdesk_id": str,
        "guest": TicketUserEvent,
        "stage": int,
        "status": int,
        "score": int,
        "created_at": int,
        "updated_at": int,
        "closed_at": int,
        "channel": int,
        "solve": int,
        "customized_fields": List[CustomizedFieldDisplayItem],
        "chat_id": str,
    }

    def __init__(self, d=None):
        self.ticket_id: Optional[str] = None
        self.helpdesk_id: Optional[str] = None
        self.guest: Optional[TicketUserEvent] = None
        self.stage: Optional[int] = None
        self.status: Optional[int] = None
        self.score: Optional[int] = None
        self.created_at: Optional[int] = None
        self.updated_at: Optional[int] = None
        self.closed_at: Optional[int] = None
        self.channel: Optional[int] = None
        self.solve: Optional[int] = None
        self.customized_fields: Optional[List[CustomizedFieldDisplayItem]] = None
        self.chat_id: Optional[str] = None
        init(self, d, self._types)


class P2HelpdeskTicketCreatedV1(EventContext):
    _types = {
        "event": P2HelpdeskTicketCreatedV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2HelpdeskTicketCreatedV1Data] = None
        init(self, d, self._types)