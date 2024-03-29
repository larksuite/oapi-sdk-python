# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .parents_department_request_body import ParentsDepartmentRequestBody


class ParentsDepartmentRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.department_id_type: Optional[str] = None
        self.request_body: Optional[ParentsDepartmentRequestBody] = None

    @staticmethod
    def builder() -> "ParentsDepartmentRequestBuilder":
        return ParentsDepartmentRequestBuilder()


class ParentsDepartmentRequestBuilder(object):

    def __init__(self) -> None:
        parents_department_request = ParentsDepartmentRequest()
        parents_department_request.http_method = HttpMethod.POST
        parents_department_request.uri = "/open-apis/corehr/v2/departments/parents"
        parents_department_request.token_types = {AccessTokenType.TENANT}
        self._parents_department_request: ParentsDepartmentRequest = parents_department_request

    def department_id_type(self, department_id_type: str) -> "ParentsDepartmentRequestBuilder":
        self._parents_department_request.department_id_type = department_id_type
        self._parents_department_request.add_query("department_id_type", department_id_type)
        return self

    def request_body(self, request_body: ParentsDepartmentRequestBody) -> "ParentsDepartmentRequestBuilder":
        self._parents_department_request.request_body = request_body
        self._parents_department_request.body = request_body
        return self

    def build(self) -> ParentsDepartmentRequest:
        return self._parents_department_request
