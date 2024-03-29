# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .eco_exam_paper import EcoExamPaper


class BatchUpdateEcoExamPaperRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.request_body: Optional[EcoExamPaper] = None

    @staticmethod
    def builder() -> "BatchUpdateEcoExamPaperRequestBuilder":
        return BatchUpdateEcoExamPaperRequestBuilder()


class BatchUpdateEcoExamPaperRequestBuilder(object):

    def __init__(self) -> None:
        batch_update_eco_exam_paper_request = BatchUpdateEcoExamPaperRequest()
        batch_update_eco_exam_paper_request.http_method = HttpMethod.PATCH
        batch_update_eco_exam_paper_request.uri = "/open-apis/hire/v1/eco_exam_papers/batch_update"
        batch_update_eco_exam_paper_request.token_types = {AccessTokenType.TENANT}
        self._batch_update_eco_exam_paper_request: BatchUpdateEcoExamPaperRequest = batch_update_eco_exam_paper_request

    def request_body(self, request_body: EcoExamPaper) -> "BatchUpdateEcoExamPaperRequestBuilder":
        self._batch_update_eco_exam_paper_request.request_body = request_body
        self._batch_update_eco_exam_paper_request.body = request_body
        return self

    def build(self) -> BatchUpdateEcoExamPaperRequest:
        return self._batch_update_eco_exam_paper_request
