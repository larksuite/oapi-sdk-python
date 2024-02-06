# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .lang_text import LangText


class PatchLeaveAccrualRecordRequestBody(object):
    _types = {
        "leave_granting_record_id": str,
        "employment_id": str,
        "leave_type_id": str,
        "reason": List[LangText],
        "time_offset": int,
        "expiration_date": str,
        "quantity": str,
    }

    def __init__(self, d=None):
        self.leave_granting_record_id: Optional[str] = None
        self.employment_id: Optional[str] = None
        self.leave_type_id: Optional[str] = None
        self.reason: Optional[List[LangText]] = None
        self.time_offset: Optional[int] = None
        self.expiration_date: Optional[str] = None
        self.quantity: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        return PatchLeaveAccrualRecordRequestBodyBuilder()


class PatchLeaveAccrualRecordRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._patch_leave_accrual_record_request_body = PatchLeaveAccrualRecordRequestBody()

    def leave_granting_record_id(self, leave_granting_record_id: str) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.leave_granting_record_id = leave_granting_record_id
        return self

    def employment_id(self, employment_id: str) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.employment_id = employment_id
        return self

    def leave_type_id(self, leave_type_id: str) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.leave_type_id = leave_type_id
        return self

    def reason(self, reason: List[LangText]) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.reason = reason
        return self

    def time_offset(self, time_offset: int) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.time_offset = time_offset
        return self

    def expiration_date(self, expiration_date: str) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.expiration_date = expiration_date
        return self

    def quantity(self, quantity: str) -> "PatchLeaveAccrualRecordRequestBodyBuilder":
        self._patch_leave_accrual_record_request_body.quantity = quantity
        return self

    def build(self) -> "PatchLeaveAccrualRecordRequestBody":
        return self._patch_leave_accrual_record_request_body