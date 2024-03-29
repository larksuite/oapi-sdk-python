# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .job_level import JobLevel


class BatchGetJobLevelResponseBody(object):
    _types = {
        "items": List[JobLevel],
    }

    def __init__(self, d=None):
        self.items: Optional[List[JobLevel]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BatchGetJobLevelResponseBodyBuilder":
        return BatchGetJobLevelResponseBodyBuilder()


class BatchGetJobLevelResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._batch_get_job_level_response_body = BatchGetJobLevelResponseBody()

    def items(self, items: List[JobLevel]) -> "BatchGetJobLevelResponseBodyBuilder":
        self._batch_get_job_level_response_body.items = items
        return self

    def build(self) -> "BatchGetJobLevelResponseBody":
        return self._batch_get_job_level_response_body
