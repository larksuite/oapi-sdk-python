# Code generated by Lark OpenAPI.

from typing import Optional, List

from lark_oapi.core.construct import init
from .agent_schedule_update_info import AgentScheduleUpdateInfo


class CreateAgentScheduleRequestBody(object):
    _types = {
        "agent_schedules": List[AgentScheduleUpdateInfo],
    }

    def __init__(self, d=None):
        self.agent_schedules: Optional[List[AgentScheduleUpdateInfo]] = None
        init(self, d, self._types)

    @staticmethod
    def builder() -> "CreateAgentScheduleRequestBodyBuilder":
        return CreateAgentScheduleRequestBodyBuilder()


class CreateAgentScheduleRequestBodyBuilder(object):
    def __init__(self) -> None:
        self._create_agent_schedule_request_body = CreateAgentScheduleRequestBody()

    def agent_schedules(self,
                        agent_schedules: List[AgentScheduleUpdateInfo]) -> "CreateAgentScheduleRequestBodyBuilder":
        self._create_agent_schedule_request_body.agent_schedules = agent_schedules
        return self

    def build(self) -> "CreateAgentScheduleRequestBody":
        return self._create_agent_schedule_request_body