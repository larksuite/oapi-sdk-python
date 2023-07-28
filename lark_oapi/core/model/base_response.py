from typing import *

from lark_oapi.core.const import X_TT_LOGID
from lark_oapi.core.construct import init
from .raw_response import RawResponse


class BaseResponse(object):
    _types = {}

    def __init__(self, d):
        self.raw: Optional[RawResponse] = None
        self.code: Optional[int] = None
        self.msg: Optional[str] = None
        init(self, d, self._types)

    def success(self):
        return self.code is not None and self.code == 0

    def get_log_id(self) -> Optional[str]:
        if self.raw is None or self.raw.headers is None:
            return None
        return self.raw.headers.get(X_TT_LOGID)
