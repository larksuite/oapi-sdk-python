# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType
from .withdraw_referral_account_request_body import WithdrawReferralAccountRequestBody


class WithdrawReferralAccountRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.referral_account_id: Optional[str] = None
        self.request_body: Optional[WithdrawReferralAccountRequestBody] = None

    @staticmethod
    def builder() -> "WithdrawReferralAccountRequestBuilder":
        return WithdrawReferralAccountRequestBuilder()


class WithdrawReferralAccountRequestBuilder(object):

    def __init__(self) -> None:
        withdraw_referral_account_request = WithdrawReferralAccountRequest()
        withdraw_referral_account_request.http_method = HttpMethod.POST
        withdraw_referral_account_request.uri = "/open-apis/hire/v1/referral_account/:referral_account_id/withdraw"
        withdraw_referral_account_request.token_types = {AccessTokenType.TENANT}
        self._withdraw_referral_account_request: WithdrawReferralAccountRequest = withdraw_referral_account_request

    def referral_account_id(self, referral_account_id: str) -> "WithdrawReferralAccountRequestBuilder":
        self._withdraw_referral_account_request.referral_account_id = referral_account_id
        self._withdraw_referral_account_request.paths["referral_account_id"] = str(referral_account_id)
        return self

    def request_body(self, request_body: WithdrawReferralAccountRequestBody) -> "WithdrawReferralAccountRequestBuilder":
        self._withdraw_referral_account_request.request_body = request_body
        self._withdraw_referral_account_request.body = request_body
        return self

    def build(self) -> WithdrawReferralAccountRequest:
        return self._withdraw_referral_account_request
