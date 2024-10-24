# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class DeleteExternalReferralRewardRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.external_referral_reward_id: Optional[str] = None

    @staticmethod
    def builder() -> "DeleteExternalReferralRewardRequestBuilder":
        return DeleteExternalReferralRewardRequestBuilder()


class DeleteExternalReferralRewardRequestBuilder(object):

    def __init__(self) -> None:
        delete_external_referral_reward_request = DeleteExternalReferralRewardRequest()
        delete_external_referral_reward_request.http_method = HttpMethod.DELETE
        delete_external_referral_reward_request.uri = "/open-apis/hire/v1/external_referral_rewards/:external_referral_reward_id"
        delete_external_referral_reward_request.token_types = {AccessTokenType.TENANT}
        self._delete_external_referral_reward_request: DeleteExternalReferralRewardRequest = delete_external_referral_reward_request

    def external_referral_reward_id(self,
                                    external_referral_reward_id: str) -> "DeleteExternalReferralRewardRequestBuilder":
        self._delete_external_referral_reward_request.external_referral_reward_id = external_referral_reward_id
        self._delete_external_referral_reward_request.paths["external_referral_reward_id"] = str(
            external_referral_reward_id)
        return self

    def build(self) -> DeleteExternalReferralRewardRequest:
        return self._delete_external_referral_reward_request