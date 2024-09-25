# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init


class BatchWorkforcePlanDetailRequestBody(object):
    _types = {
        "workforce_plan_id": str,
        "is_centralized_reporting_project": bool,
        "centralized_reporting_project_id": str,
        "department_ids": List[str],
        "employee_type_ids": List[str],
        "work_location_ids": List[str],
        "job_family_ids": List[str],
        "job_level_ids": List[str],
        "job_ids": List[str],
        "cost_center_ids": List[str],
    }

    def __init__(self, d=None):
        self.workforce_plan_id: Optional[str] = None
        self.is_centralized_reporting_project: Optional[bool] = None
        self.centralized_reporting_project_id: Optional[str] = None
        self.department_ids: Optional[List[str]] = None
        self.employee_type_ids: Optional[List[str]] = None
        self.work_location_ids: Optional[List[str]] = None
        self.job_family_ids: Optional[List[str]] = None
        self.job_level_ids: Optional[List[str]] = None
        self.job_ids: Optional[List[str]] = None
        self.cost_center_ids: Optional[List[str]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        return BatchWorkforcePlanDetailRequestBodyBuilder()


class BatchWorkforcePlanDetailRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._batch_workforce_plan_detail_request_body = BatchWorkforcePlanDetailRequestBody()

    def workforce_plan_id(self, workforce_plan_id: str) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.workforce_plan_id = workforce_plan_id
        return self

    def is_centralized_reporting_project(self,
                                         is_centralized_reporting_project: bool) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.is_centralized_reporting_project = is_centralized_reporting_project
        return self

    def centralized_reporting_project_id(self,
                                         centralized_reporting_project_id: str) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.centralized_reporting_project_id = centralized_reporting_project_id
        return self

    def department_ids(self, department_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.department_ids = department_ids
        return self

    def employee_type_ids(self, employee_type_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.employee_type_ids = employee_type_ids
        return self

    def work_location_ids(self, work_location_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.work_location_ids = work_location_ids
        return self

    def job_family_ids(self, job_family_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.job_family_ids = job_family_ids
        return self

    def job_level_ids(self, job_level_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.job_level_ids = job_level_ids
        return self

    def job_ids(self, job_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.job_ids = job_ids
        return self

    def cost_center_ids(self, cost_center_ids: List[str]) -> "BatchWorkforcePlanDetailRequestBodyBuilder":
        self._batch_workforce_plan_detail_request_body.cost_center_ids = cost_center_ids
        return self

    def build(self) -> "BatchWorkforcePlanDetailRequestBody":
        return self._batch_workforce_plan_detail_request_body
