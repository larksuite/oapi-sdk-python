# Code generated by Lark OpenAPI.

from typing import Callable, Type

from lark_oapi.event.processor import IEventProcessor
from .model.p2_hire_application_stage_changed_v1 import P2HireApplicationStageChangedV1
from .model.p2_hire_ehr_import_task_for_internship_offer_imported_v1 import \
    P2HireEhrImportTaskForInternshipOfferImportedV1
from .model.p2_hire_ehr_import_task_imported_v1 import P2HireEhrImportTaskImportedV1
from .model.p2_hire_offer_status_changed_v1 import P2HireOfferStatusChangedV1


class P2HireApplicationStageChangedV1Processor(IEventProcessor[P2HireApplicationStageChangedV1]):
    def __init__(self, f: Callable[[P2HireApplicationStageChangedV1], None]):
        self.f = f

    def type(self) -> Type[P2HireApplicationStageChangedV1]:
        return P2HireApplicationStageChangedV1

    def do(self, data: P2HireApplicationStageChangedV1) -> None:
        self.f(data)


class P2HireEhrImportTaskImportedV1Processor(IEventProcessor[P2HireEhrImportTaskImportedV1]):
    def __init__(self, f: Callable[[P2HireEhrImportTaskImportedV1], None]):
        self.f = f

    def type(self) -> Type[P2HireEhrImportTaskImportedV1]:
        return P2HireEhrImportTaskImportedV1

    def do(self, data: P2HireEhrImportTaskImportedV1) -> None:
        self.f(data)


class P2HireEhrImportTaskForInternshipOfferImportedV1Processor(
    IEventProcessor[P2HireEhrImportTaskForInternshipOfferImportedV1]):
    def __init__(self, f: Callable[[P2HireEhrImportTaskForInternshipOfferImportedV1], None]):
        self.f = f

    def type(self) -> Type[P2HireEhrImportTaskForInternshipOfferImportedV1]:
        return P2HireEhrImportTaskForInternshipOfferImportedV1

    def do(self, data: P2HireEhrImportTaskForInternshipOfferImportedV1) -> None:
        self.f(data)


class P2HireOfferStatusChangedV1Processor(IEventProcessor[P2HireOfferStatusChangedV1]):
    def __init__(self, f: Callable[[P2HireOfferStatusChangedV1], None]):
        self.f = f

    def type(self) -> Type[P2HireOfferStatusChangedV1]:
        return P2HireOfferStatusChangedV1

    def do(self, data: P2HireOfferStatusChangedV1) -> None:
        self.f(data)
