# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class ResumeCareer(object):
    _types = {
        "company": str,
        "start_date": str,
        "start_time": str,
        "end_date": str,
        "end_time": str,
        "title": str,
        "type": int,
        "type_str": str,
        "job_description": str,
    }

    def __init__(self, d=None):
        self.company: Optional[str] = None
        self.start_date: Optional[str] = None
        self.start_time: Optional[str] = None
        self.end_date: Optional[str] = None
        self.end_time: Optional[str] = None
        self.title: Optional[str] = None
        self.type: Optional[int] = None
        self.type_str: Optional[str] = None
        self.job_description: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ResumeCareerBuilder":
        return ResumeCareerBuilder()


class ResumeCareerBuilder(object):
    def __init__(self) -> None:
        self._resume_career = ResumeCareer()

    def company(self, company: str) -> "ResumeCareerBuilder":
        self._resume_career.company = company
        return self

    def start_date(self, start_date: str) -> "ResumeCareerBuilder":
        self._resume_career.start_date = start_date
        return self

    def start_time(self, start_time: str) -> "ResumeCareerBuilder":
        self._resume_career.start_time = start_time
        return self

    def end_date(self, end_date: str) -> "ResumeCareerBuilder":
        self._resume_career.end_date = end_date
        return self

    def end_time(self, end_time: str) -> "ResumeCareerBuilder":
        self._resume_career.end_time = end_time
        return self

    def title(self, title: str) -> "ResumeCareerBuilder":
        self._resume_career.title = title
        return self

    def type(self, type: int) -> "ResumeCareerBuilder":
        self._resume_career.type = type
        return self

    def type_str(self, type_str: str) -> "ResumeCareerBuilder":
        self._resume_career.type_str = type_str
        return self

    def job_description(self, job_description: str) -> "ResumeCareerBuilder":
        self._resume_career.job_description = job_description
        return self

    def build(self) -> "ResumeCareer":
        return self._resume_career
