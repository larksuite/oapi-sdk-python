# Code generated by Lark OpenAPI.

from typing import Callable, Type

from lark_oapi.event.processor import IEventProcessor
from .model.p2_acs_access_record_created_v1 import P2AcsAccessRecordCreatedV1
from .model.p2_acs_user_updated_v1 import P2AcsUserUpdatedV1


class P2AcsAccessRecordCreatedV1Processor(IEventProcessor[P2AcsAccessRecordCreatedV1]):
    def __init__(self, f: Callable[[P2AcsAccessRecordCreatedV1], None]):
        self.f = f

    def type(self) -> Type[P2AcsAccessRecordCreatedV1]:
        return P2AcsAccessRecordCreatedV1

    def do(self, data: P2AcsAccessRecordCreatedV1) -> None:
        self.f(data)


class P2AcsUserUpdatedV1Processor(IEventProcessor[P2AcsUserUpdatedV1]):
    def __init__(self, f: Callable[[P2AcsUserUpdatedV1], None]):
        self.f = f

    def type(self) -> Type[P2AcsUserUpdatedV1]:
        return P2AcsUserUpdatedV1

    def do(self, data: P2AcsUserUpdatedV1) -> None:
        self.f(data)
