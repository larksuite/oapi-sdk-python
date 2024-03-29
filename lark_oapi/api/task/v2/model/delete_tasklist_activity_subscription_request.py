# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class DeleteTasklistActivitySubscriptionRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()
        self.tasklist_guid: Optional[str] = None
        self.activity_subscription_guid: Optional[str] = None

    @staticmethod
    def builder() -> "DeleteTasklistActivitySubscriptionRequestBuilder":
        return DeleteTasklistActivitySubscriptionRequestBuilder()


class DeleteTasklistActivitySubscriptionRequestBuilder(object):

    def __init__(self) -> None:
        delete_tasklist_activity_subscription_request = DeleteTasklistActivitySubscriptionRequest()
        delete_tasklist_activity_subscription_request.http_method = HttpMethod.DELETE
        delete_tasklist_activity_subscription_request.uri = "/open-apis/task/v2/tasklists/:tasklist_guid/activity_subscriptions/:activity_subscription_guid"
        delete_tasklist_activity_subscription_request.token_types = {AccessTokenType.TENANT, AccessTokenType.USER}
        self._delete_tasklist_activity_subscription_request: DeleteTasklistActivitySubscriptionRequest = delete_tasklist_activity_subscription_request

    def tasklist_guid(self, tasklist_guid: str) -> "DeleteTasklistActivitySubscriptionRequestBuilder":
        self._delete_tasklist_activity_subscription_request.tasklist_guid = tasklist_guid
        self._delete_tasklist_activity_subscription_request.paths["tasklist_guid"] = str(tasklist_guid)
        return self

    def activity_subscription_guid(self,
                                   activity_subscription_guid: str) -> "DeleteTasklistActivitySubscriptionRequestBuilder":
        self._delete_tasklist_activity_subscription_request.activity_subscription_guid = activity_subscription_guid
        self._delete_tasklist_activity_subscription_request.paths["activity_subscription_guid"] = str(
            activity_subscription_guid)
        return self

    def build(self) -> DeleteTasklistActivitySubscriptionRequest:
        return self._delete_tasklist_activity_subscription_request
