# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class RecognizeTwMainlandTravelPermitRequestBody(object):
    _types = {
        "file": IO[Any],
    }

    def __init__(self, d=None):
        self.file: Optional[IO[Any]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "RecognizeTwMainlandTravelPermitRequestBodyBuilder":
        return RecognizeTwMainlandTravelPermitRequestBodyBuilder()


class RecognizeTwMainlandTravelPermitRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._recognize_tw_mainland_travel_permit_request_body = RecognizeTwMainlandTravelPermitRequestBody()

    def file(self, file: IO[Any]) -> "RecognizeTwMainlandTravelPermitRequestBodyBuilder":
        self._recognize_tw_mainland_travel_permit_request_body.file = file
        return self

    def build(self) -> "RecognizeTwMainlandTravelPermitRequestBody":
        return self._recognize_tw_mainland_travel_permit_request_body
