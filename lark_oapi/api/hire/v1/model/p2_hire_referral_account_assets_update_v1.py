# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from lark_oapi.event.context import EventContext
from .assets import Assets


class P2HireReferralAccountAssetsUpdateV1Data(object):
    _types = {
        "account_id": str,
        "assets": Assets,
        "modify_time": str,
    }

    def __init__(self, d=None):
        self.account_id: Optional[str] = None
        self.assets: Optional[Assets] = None
        self.modify_time: Optional[str] = None
        init(self, d, self._types)


class P2HireReferralAccountAssetsUpdateV1(EventContext):
    _types = {
        "event": P2HireReferralAccountAssetsUpdateV1Data
    }

    def __init__(self, d=None):
        super().__init__(d)
        self._types.update(super()._types)
        self.event: Optional[P2HireReferralAccountAssetsUpdateV1Data] = None
        init(self, d, self._types)
