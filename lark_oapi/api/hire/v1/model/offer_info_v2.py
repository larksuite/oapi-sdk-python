# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .offer_basic_info_v2 import OfferBasicInfoV2
from .offer_salary_info_v2 import OfferSalaryInfoV2


class OfferInfoV2(object):
    _types = {
        "offer_basic": OfferBasicInfoV2,
        "offer_salary": OfferSalaryInfoV2,
    }

    def __init__(self, d=None):
        self.offer_basic: Optional[OfferBasicInfoV2] = None
        self.offer_salary: Optional[OfferSalaryInfoV2] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "OfferInfoV2Builder":
        return OfferInfoV2Builder()


class OfferInfoV2Builder(object):
    def __init__(self) -> None:
        self._offer_info_v2 = OfferInfoV2()

    def offer_basic(self, offer_basic: OfferBasicInfoV2) -> "OfferInfoV2Builder":
        self._offer_info_v2.offer_basic = offer_basic
        return self

    def offer_salary(self, offer_salary: OfferSalaryInfoV2) -> "OfferInfoV2Builder":
        self._offer_info_v2.offer_salary = offer_salary
        return self

    def build(self) -> "OfferInfoV2":
        return self._offer_info_v2
