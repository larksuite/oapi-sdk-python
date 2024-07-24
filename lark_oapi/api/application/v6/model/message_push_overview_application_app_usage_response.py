# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.core.model import BaseResponse
from .message_push_overview_application_app_usage_response_body import \
    MessagePushOverviewApplicationAppUsageResponseBody


class MessagePushOverviewApplicationAppUsageResponse(BaseResponse):
    _types = {
        "data": MessagePushOverviewApplicationAppUsageResponseBody
    }

    def __init__(self, d=None):
        super().__init__(d)
        self.data: Optional[MessagePushOverviewApplicationAppUsageResponseBody] = None
        init(self, d, self._types)
