# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from .delete_record import DeleteRecord


class BatchDeleteAppTableRecordResponseBody(object):
    _types = {
        "records": List[DeleteRecord],
    }

    def __init__(self, d):
        self.records: Optional[List[DeleteRecord]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BatchDeleteAppTableRecordResponseBodyBuilder":
        return BatchDeleteAppTableRecordResponseBodyBuilder()


class BatchDeleteAppTableRecordResponseBodyBuilder(object):
    def __init__(self, batch_delete_app_table_record_response_body: BatchDeleteAppTableRecordResponseBody = BatchDeleteAppTableRecordResponseBody({})) -> None:
        self._batch_delete_app_table_record_response_body: BatchDeleteAppTableRecordResponseBody = batch_delete_app_table_record_response_body
    
    def records(self, records: List[DeleteRecord]) -> "BatchDeleteAppTableRecordResponseBodyBuilder":
        self._batch_delete_app_table_record_response_body.records = records
        return self
    
    def build(self) -> "BatchDeleteAppTableRecordResponseBody":
        return self._batch_delete_app_table_record_response_body