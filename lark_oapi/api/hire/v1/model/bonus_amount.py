# Code generated by Lark OpenAPI.

from typing import Optional

from lark_oapi.core.construct import init


class BonusAmount(object):
    _types = {
        "point_bonus": int,
    }

    def __init__(self, d=None):
        self.point_bonus: Optional[int] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "BonusAmountBuilder":
        return BonusAmountBuilder()


class BonusAmountBuilder(object):
    def __init__(self) -> None:
        self._bonus_amount = BonusAmount()

    def point_bonus(self, point_bonus: int) -> "BonusAmountBuilder":
        self._bonus_amount.point_bonus = point_bonus
        return self

    def build(self) -> "BonusAmount":
        return self._bonus_amount