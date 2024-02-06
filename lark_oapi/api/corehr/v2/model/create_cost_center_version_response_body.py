# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init
from .cost_center_version import CostCenterVersion


class CreateCostCenterVersionResponseBody(object):
    _types = {
        "version": CostCenterVersion,
    }

    def __init__(self, d=None):
        self.version: Optional[CostCenterVersion] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateCostCenterVersionResponseBodyBuilder":
        return CreateCostCenterVersionResponseBodyBuilder()


class CreateCostCenterVersionResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._create_cost_center_version_response_body = CreateCostCenterVersionResponseBody()

    def version(self, version: CostCenterVersion) -> "CreateCostCenterVersionResponseBodyBuilder":
        self._create_cost_center_version_response_body.version = version
        return self

    def build(self) -> "CreateCostCenterVersionResponseBody":
        return self._create_cost_center_version_response_body