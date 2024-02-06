# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .job_family import JobFamily


class UpdateJobFamilyResponseBody(object):
    _types = {
        "job_family": JobFamily,
    }

    def __init__(self, d=None):
        self.job_family: Optional[JobFamily] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "UpdateJobFamilyResponseBodyBuilder":
        return UpdateJobFamilyResponseBodyBuilder()


class UpdateJobFamilyResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._update_job_family_response_body = UpdateJobFamilyResponseBody()

    def job_family(self, job_family: JobFamily) -> "UpdateJobFamilyResponseBodyBuilder":
        self._update_job_family_response_body.job_family = job_family
        return self

    def build(self) -> "UpdateJobFamilyResponseBody":
        return self._update_job_family_response_body