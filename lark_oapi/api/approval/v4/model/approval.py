# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init


class Approval(object):
    _types = {
        "approval_code": str,
        "approval_name": str,
        "status": str,
    }

    def __init__(self, d):
        self.approval_code: Optional[str] = None
        self.approval_name: Optional[str] = None
        self.status: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ApprovalBuilder":
        return ApprovalBuilder()


class ApprovalBuilder(object):
    def __init__(self, approval: Approval = Approval({})) -> None:
        self._approval: Approval = approval
    
    def approval_code(self, approval_code: str) -> "ApprovalBuilder":
        self._approval.approval_code = approval_code
        return self
    
    def approval_name(self, approval_name: str) -> "ApprovalBuilder":
        self._approval.approval_name = approval_name
        return self
    
    def status(self, status: str) -> "ApprovalBuilder":
        self._approval.status = status
        return self
    
    def build(self) -> "Approval":
        return self._approval