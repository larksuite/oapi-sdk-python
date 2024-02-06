# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class ParticipantListExportResponseBody(object):
    _types = {
        "task_id": str,
    }

    def __init__(self, d=None):
        self.task_id: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "ParticipantListExportResponseBodyBuilder":
        return ParticipantListExportResponseBodyBuilder()


class ParticipantListExportResponseBodyBuilder(object):
    def __init__(self) -> None:
        self._participant_list_export_response_body = ParticipantListExportResponseBody()

    def task_id(self, task_id: str) -> "ParticipantListExportResponseBodyBuilder":
        self._participant_list_export_response_body.task_id = task_id
        return self

    def build(self) -> "ParticipantListExportResponseBody":
        return self._participant_list_export_response_body