# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.construct import init
from .food_manage_entity import FoodManageEntity


class FoodManageLicense(object):
    _types = {
        "entities": List[FoodManageEntity],
    }

    def __init__(self, d=None):
        self.entities: Optional[List[FoodManageEntity]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "FoodManageLicenseBuilder":
        return FoodManageLicenseBuilder()


class FoodManageLicenseBuilder(object):
    def __init__(self) -> None:
        self._food_manage_license = FoodManageLicense()

    def entities(self, entities: List[FoodManageEntity]) -> "FoodManageLicenseBuilder":
        self._food_manage_license.entities = entities
        return self

    def build(self) -> "FoodManageLicense":
        return self._food_manage_license
