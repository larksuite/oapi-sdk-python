# Code generated by Lark OpenAPI.

from typing import *
from typing import IO
from lark_oapi.core.construct import init
from .bonus_amount import BonusAmount
from .bonus_amount import BonusAmount


class CheckFailedAccountInfo(object):
    _types = {
        "account_id": str,
        "total_withdraw_reward_info": BonusAmount,
        "total_recharge_reward_info": BonusAmount,
    }

    def __init__(self, d):
        self.account_id: Optional[str] = None
        self.total_withdraw_reward_info: Optional[BonusAmount] = None
        self.total_recharge_reward_info: Optional[BonusAmount] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CheckFailedAccountInfoBuilder":
        return CheckFailedAccountInfoBuilder()


class CheckFailedAccountInfoBuilder(object):
    def __init__(self, check_failed_account_info: CheckFailedAccountInfo = CheckFailedAccountInfo({})) -> None:
        self._check_failed_account_info: CheckFailedAccountInfo = check_failed_account_info
    
    def account_id(self, account_id: str) -> "CheckFailedAccountInfoBuilder":
        self._check_failed_account_info.account_id = account_id
        return self
    
    def total_withdraw_reward_info(self, total_withdraw_reward_info: BonusAmount) -> "CheckFailedAccountInfoBuilder":
        self._check_failed_account_info.total_withdraw_reward_info = total_withdraw_reward_info
        return self
    
    def total_recharge_reward_info(self, total_recharge_reward_info: BonusAmount) -> "CheckFailedAccountInfoBuilder":
        self._check_failed_account_info.total_recharge_reward_info = total_recharge_reward_info
        return self
    
    def build(self) -> "CheckFailedAccountInfo":
        return self._check_failed_account_info