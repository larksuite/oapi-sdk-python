# Code generated by Lark OpenAPI.

from typing import Callable, Type

from lark_oapi.event.processor import IEventProcessor
from .model.p2_corehr_probation_updated_v2 import P2CorehrProbationUpdatedV2
from .model.p2_corehr_process_approver_updated_v2 import P2CorehrProcessApproverUpdatedV2
from .model.p2_corehr_process_cc_updated_v2 import P2CorehrProcessCcUpdatedV2
from .model.p2_corehr_process_updated_v2 import P2CorehrProcessUpdatedV2


class P2CorehrProbationUpdatedV2Processor(IEventProcessor[P2CorehrProbationUpdatedV2]):
    def __init__(self, f: Callable[[P2CorehrProbationUpdatedV2], None]):
        self.f = f

    def type(self) -> Type[P2CorehrProbationUpdatedV2]:
        return P2CorehrProbationUpdatedV2

    def do(self, data: P2CorehrProbationUpdatedV2) -> None:
        self.f(data)


class P2CorehrProcessUpdatedV2Processor(IEventProcessor[P2CorehrProcessUpdatedV2]):
    def __init__(self, f: Callable[[P2CorehrProcessUpdatedV2], None]):
        self.f = f

    def type(self) -> Type[P2CorehrProcessUpdatedV2]:
        return P2CorehrProcessUpdatedV2

    def do(self, data: P2CorehrProcessUpdatedV2) -> None:
        self.f(data)


class P2CorehrProcessApproverUpdatedV2Processor(IEventProcessor[P2CorehrProcessApproverUpdatedV2]):
    def __init__(self, f: Callable[[P2CorehrProcessApproverUpdatedV2], None]):
        self.f = f

    def type(self) -> Type[P2CorehrProcessApproverUpdatedV2]:
        return P2CorehrProcessApproverUpdatedV2

    def do(self, data: P2CorehrProcessApproverUpdatedV2) -> None:
        self.f(data)


class P2CorehrProcessCcUpdatedV2Processor(IEventProcessor[P2CorehrProcessCcUpdatedV2]):
    def __init__(self, f: Callable[[P2CorehrProcessCcUpdatedV2], None]):
        self.f = f

    def type(self) -> Type[P2CorehrProcessCcUpdatedV2]:
        return P2CorehrProcessCcUpdatedV2

    def do(self, data: P2CorehrProcessCcUpdatedV2) -> None:
        self.f(data)