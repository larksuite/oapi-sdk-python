# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext


class P2CorehrJobLevelDeletedV2Data(object):
    _types = {
        "job_level_id": str,
    }

    def __init__(self, d=None):
        self.job_level_id: Optional[str] = None
        init(self, d, self._types)


class P2CorehrJobLevelDeletedV2(EventContext):
    _types = {
        "event": P2CorehrJobLevelDeletedV2Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2CorehrJobLevelDeletedV2Data] = None
        init(self, d, self._types)
