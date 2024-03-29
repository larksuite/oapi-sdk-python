# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .hkm_mainland_travel_permit import HkmMainlandTravelPermit


class RecognizeHkmMainlandTravelPermitResponseBody(object):
    _types = {
        "hkm_mainland_travel_permit": HkmMainlandTravelPermit,
    }

    def __init__(self, d=None):
        self.hkm_mainland_travel_permit: Optional[HkmMainlandTravelPermit] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RecognizeHkmMainlandTravelPermitResponseBodyBuilder":
        return RecognizeHkmMainlandTravelPermitResponseBodyBuilder()


class RecognizeHkmMainlandTravelPermitResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._recognize_hkm_mainland_travel_permit_response_body = RecognizeHkmMainlandTravelPermitResponseBody()

    def hkm_mainland_travel_permit(self,
                                   hkm_mainland_travel_permit: HkmMainlandTravelPermit) -> "RecognizeHkmMainlandTravelPermitResponseBodyBuilder":
        self._recognize_hkm_mainland_travel_permit_response_body.hkm_mainland_travel_permit = hkm_mainland_travel_permit
        return self

    def build(self) -> "RecognizeHkmMainlandTravelPermitResponseBody":
        return self._recognize_hkm_mainland_travel_permit_response_body
