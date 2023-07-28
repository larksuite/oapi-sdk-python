# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .user_id import UserId


class P2ApplicationApplicationAppVersionAuditV6Data(object):
    _types = {
        "operator_id": UserId,
        "version_id": str,
        "creator_id": UserId,
        "app_id": str,
        "operation": str,
        "remark": str,
        "audit_source": str,
    }

    def __init__(self, d=None):
        self.operator_id: Optional[UserId] = None
        self.version_id: Optional[str] = None
        self.creator_id: Optional[UserId] = None
        self.app_id: Optional[str] = None
        self.operation: Optional[str] = None
        self.remark: Optional[str] = None
        self.audit_source: Optional[str] = None
        init(self, d, self._types)


class P2ApplicationApplicationAppVersionAuditV6(EventContext):
    _types = {
        "event": P2ApplicationApplicationAppVersionAuditV6Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2ApplicationApplicationAppVersionAuditV6Data] = None
        init(self, d, self._types)
