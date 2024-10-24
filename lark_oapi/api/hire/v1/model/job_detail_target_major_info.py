# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .i18n import I18n


class JobDetailTargetMajorInfo(object):
    _types = {
        "id": str,
        "name": I18n,
    }

    def __init__(self, d=None):
        self.id: Optional[str] = None
        self.name: Optional[I18n] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "JobDetailTargetMajorInfoBuilder":
        return JobDetailTargetMajorInfoBuilder()


class JobDetailTargetMajorInfoBuilder(object):
    def __init__(self) -> None:
        self._job_detail_target_major_info = JobDetailTargetMajorInfo()

    def id(self, id: str) -> "JobDetailTargetMajorInfoBuilder":
        self._job_detail_target_major_info.id = id
        return self

    def name(self, name: I18n) -> "JobDetailTargetMajorInfoBuilder":
        self._job_detail_target_major_info.name = name
        return self

    def build(self) -> "JobDetailTargetMajorInfo":
        return self._job_detail_target_major_info
