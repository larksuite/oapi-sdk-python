# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .dlp_evidence_detail import DlpEvidenceDetail
from .dlp_hit_policy import DlpHitPolicy


class DlpExecuteLog(object):
    _types = {
        "applicable_service": str,
        "user_name": str,
        "user_id": int,
        "trigger": str,
        "time": int,
        "system_action": str,
        "sender_name": str,
        "sender_id": int,
        "recipient_name": str,
        "recipient_id": int,
        "chat_name": str,
        "chat_id": int,
        "message_id": int,
        "message_content": str,
        "alias_ingroup": str,
        "group_description": str,
        "group_tab_content": str,
        "file_name": str,
        "file_key": str,
        "document_owner_name": str,
        "document_owner_id": int,
        "document_name": str,
        "document_type": str,
        "document_link": str,
        "evidence_detail": DlpEvidenceDetail,
        "hit_policies": List[DlpHitPolicy],
        "file_token": str,
    }

    def __init__(self, d=None):
        self.applicable_service: Optional[str] = None
        self.user_name: Optional[str] = None
        self.user_id: Optional[int] = None
        self.trigger: Optional[str] = None
        self.time: Optional[int] = None
        self.system_action: Optional[str] = None
        self.sender_name: Optional[str] = None
        self.sender_id: Optional[int] = None
        self.recipient_name: Optional[str] = None
        self.recipient_id: Optional[int] = None
        self.chat_name: Optional[str] = None
        self.chat_id: Optional[int] = None
        self.message_id: Optional[int] = None
        self.message_content: Optional[str] = None
        self.alias_ingroup: Optional[str] = None
        self.group_description: Optional[str] = None
        self.group_tab_content: Optional[str] = None
        self.file_name: Optional[str] = None
        self.file_key: Optional[str] = None
        self.document_owner_name: Optional[str] = None
        self.document_owner_id: Optional[int] = None
        self.document_name: Optional[str] = None
        self.document_type: Optional[str] = None
        self.document_link: Optional[str] = None
        self.evidence_detail: Optional[DlpEvidenceDetail] = None
        self.hit_policies: Optional[List[DlpHitPolicy]] = None
        self.file_token: Optional[str] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "DlpExecuteLogBuilder":
        return DlpExecuteLogBuilder()


class DlpExecuteLogBuilder(object):
    def __init__(self) -> None:
        self._dlp_execute_log = DlpExecuteLog()

    def applicable_service(self, applicable_service: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.applicable_service = applicable_service
        return self

    def user_name(self, user_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.user_name = user_name
        return self

    def user_id(self, user_id: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.user_id = user_id
        return self

    def trigger(self, trigger: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.trigger = trigger
        return self

    def time(self, time: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.time = time
        return self

    def system_action(self, system_action: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.system_action = system_action
        return self

    def sender_name(self, sender_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.sender_name = sender_name
        return self

    def sender_id(self, sender_id: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.sender_id = sender_id
        return self

    def recipient_name(self, recipient_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.recipient_name = recipient_name
        return self

    def recipient_id(self, recipient_id: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.recipient_id = recipient_id
        return self

    def chat_name(self, chat_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.chat_name = chat_name
        return self

    def chat_id(self, chat_id: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.chat_id = chat_id
        return self

    def message_id(self, message_id: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.message_id = message_id
        return self

    def message_content(self, message_content: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.message_content = message_content
        return self

    def alias_ingroup(self, alias_ingroup: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.alias_ingroup = alias_ingroup
        return self

    def group_description(self, group_description: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.group_description = group_description
        return self

    def group_tab_content(self, group_tab_content: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.group_tab_content = group_tab_content
        return self

    def file_name(self, file_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.file_name = file_name
        return self

    def file_key(self, file_key: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.file_key = file_key
        return self

    def document_owner_name(self, document_owner_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.document_owner_name = document_owner_name
        return self

    def document_owner_id(self, document_owner_id: int) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.document_owner_id = document_owner_id
        return self

    def document_name(self, document_name: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.document_name = document_name
        return self

    def document_type(self, document_type: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.document_type = document_type
        return self

    def document_link(self, document_link: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.document_link = document_link
        return self

    def evidence_detail(self, evidence_detail: DlpEvidenceDetail) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.evidence_detail = evidence_detail
        return self

    def hit_policies(self, hit_policies: List[DlpHitPolicy]) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.hit_policies = hit_policies
        return self

    def file_token(self, file_token: str) -> "DlpExecuteLogBuilder":
        self._dlp_execute_log.file_token = file_token
        return self

    def build(self) -> "DlpExecuteLog":
        return self._dlp_execute_log