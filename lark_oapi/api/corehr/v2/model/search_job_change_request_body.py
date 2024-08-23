# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class SearchJobChangeRequestBody(object):
    _types = {
        "employment_ids": List[str],
        "job_change_ids": List[str],
        "statuses": List[str],
        "effective_date_start": str,
        "effective_date_end": str,
        "updated_time_start": str,
        "updated_time_end": str,
        "target_department_ids": List[str],
    }

    def __init__(self, d=None):
        self.employment_ids: Optional[List[str]] = None
        self.job_change_ids: Optional[List[str]] = None
        self.statuses: Optional[List[str]] = None
        self.effective_date_start: Optional[str] = None
        self.effective_date_end: Optional[str] = None
        self.updated_time_start: Optional[str] = None
        self.updated_time_end: Optional[str] = None
        self.target_department_ids: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "SearchJobChangeRequestBodyBuilder":
        return SearchJobChangeRequestBodyBuilder()


class SearchJobChangeRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._search_job_change_request_body = SearchJobChangeRequestBody()

    def employment_ids(self, employment_ids: List[str]) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.employment_ids = employment_ids
        return self

    def job_change_ids(self, job_change_ids: List[str]) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.job_change_ids = job_change_ids
        return self

    def statuses(self, statuses: List[str]) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.statuses = statuses
        return self

    def effective_date_start(self, effective_date_start: str) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.effective_date_start = effective_date_start
        return self

    def effective_date_end(self, effective_date_end: str) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.effective_date_end = effective_date_end
        return self

    def updated_time_start(self, updated_time_start: str) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.updated_time_start = updated_time_start
        return self

    def updated_time_end(self, updated_time_end: str) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.updated_time_end = updated_time_end
        return self

    def target_department_ids(self, target_department_ids: List[str]) -> "SearchJobChangeRequestBodyBuilder":
        self._search_job_change_request_body.target_department_ids = target_department_ids
        return self

    def build(self) -> "SearchJobChangeRequestBody":
        return self._search_job_change_request_body
