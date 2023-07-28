# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext


class P2HireApplicationStageChangedV1Data(object):
    _types = {
        "application_id": str,
        "origin_stage_id": str,
        "target_stage_id": str,
        "update_time": int,
    }

    def __init__(self, d=None):
        self.application_id: Optional[str] = None
        self.origin_stage_id: Optional[str] = None
        self.target_stage_id: Optional[str] = None
        self.update_time: Optional[int] = None
        init(self, d, self._types)


class P2HireApplicationStageChangedV1(EventContext):
    _types = {
        "event": P2HireApplicationStageChangedV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2HireApplicationStageChangedV1Data] = None
        init(self, d, self._types)
