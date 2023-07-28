# Code generated by Lark OpenAPI.

from typing import Callable, Type

from lark_oapi.event.processor import IEventProcessor
from .model.p2_helpdesk_notification_approve_v1 import P2HelpdeskNotificationApproveV1
from .model.p2_helpdesk_ticket_created_v1 import P2HelpdeskTicketCreatedV1
from .model.p2_helpdesk_ticket_message_created_v1 import P2HelpdeskTicketMessageCreatedV1
from .model.p2_helpdesk_ticket_updated_v1 import P2HelpdeskTicketUpdatedV1


class P2HelpdeskNotificationApproveV1Processor(IEventProcessor[P2HelpdeskNotificationApproveV1]):
    def __init__(self, f: Callable[[P2HelpdeskNotificationApproveV1], None]):
        self.f = f

    def type(self) -> Type[P2HelpdeskNotificationApproveV1]:
        return P2HelpdeskNotificationApproveV1

    def do(self, data: P2HelpdeskNotificationApproveV1) -> None:
        self.f(data)


class P2HelpdeskTicketCreatedV1Processor(IEventProcessor[P2HelpdeskTicketCreatedV1]):
    def __init__(self, f: Callable[[P2HelpdeskTicketCreatedV1], None]):
        self.f = f

    def type(self) -> Type[P2HelpdeskTicketCreatedV1]:
        return P2HelpdeskTicketCreatedV1

    def do(self, data: P2HelpdeskTicketCreatedV1) -> None:
        self.f(data)


class P2HelpdeskTicketUpdatedV1Processor(IEventProcessor[P2HelpdeskTicketUpdatedV1]):
    def __init__(self, f: Callable[[P2HelpdeskTicketUpdatedV1], None]):
        self.f = f

    def type(self) -> Type[P2HelpdeskTicketUpdatedV1]:
        return P2HelpdeskTicketUpdatedV1

    def do(self, data: P2HelpdeskTicketUpdatedV1) -> None:
        self.f(data)


class P2HelpdeskTicketMessageCreatedV1Processor(IEventProcessor[P2HelpdeskTicketMessageCreatedV1]):
    def __init__(self, f: Callable[[P2HelpdeskTicketMessageCreatedV1], None]):
        self.f = f

    def type(self) -> Type[P2HelpdeskTicketMessageCreatedV1]:
        return P2HelpdeskTicketMessageCreatedV1

    def do(self, data: P2HelpdeskTicketMessageCreatedV1) -> None:
        self.f(data)
