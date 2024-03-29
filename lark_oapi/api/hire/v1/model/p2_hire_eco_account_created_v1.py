# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .eco_account_custom_field_event_data import EcoAccountCustomFieldEventData


class P2HireEcoAccountCreatedV1Data(object):
    _types = {
        "scope": int,
        "account_id": str,
        "account_name": str,
        "usage_list": List[int],
        "custom_field_list": List[EcoAccountCustomFieldEventData],
    }

    def __init__(self, d=None):
        self.scope: Optional[int] = None
        self.account_id: Optional[str] = None
        self.account_name: Optional[str] = None
        self.usage_list: Optional[List[int]] = None
        self.custom_field_list: Optional[List[EcoAccountCustomFieldEventData]] = None
        init(self, d, self._types)


class P2HireEcoAccountCreatedV1(EventContext):
    _types = {
        "event": P2HireEcoAccountCreatedV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2HireEcoAccountCreatedV1Data] = None
        init(self, d, self._types)
