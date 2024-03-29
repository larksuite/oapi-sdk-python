# Code generated by Lark OpenAPI.

from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.model import BaseRequest
from lark_oapi.core.enum import HttpMethod, AccessTokenType


class AgentEmailAgentRequest(BaseRequest):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def builder() -> "AgentEmailAgentRequestBuilder":
        return AgentEmailAgentRequestBuilder()


class AgentEmailAgentRequestBuilder(object):

    def __init__(self) -> None:
        agent_email_agent_request = AgentEmailAgentRequest()
        agent_email_agent_request.http_method = HttpMethod.GET
        agent_email_agent_request.uri = "/open-apis/helpdesk/v1/agent_emails"
        agent_email_agent_request.token_types = {AccessTokenType.TENANT}
        self._agent_email_agent_request: AgentEmailAgentRequest = agent_email_agent_request

    def build(self) -> AgentEmailAgentRequest:
        return self._agent_email_agent_request
