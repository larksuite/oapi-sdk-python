# Code generated by Lark OpenAPI.

from typing import *

from lark_oapi.core import JSON
from lark_oapi.core.const import UTF_8
from lark_oapi.core.http import Transport
from lark_oapi.core.model import Config, RequestOption, RawResponse
from lark_oapi.core.token import verify
from ..model.create_task_subtask_request import CreateTaskSubtaskRequest
from ..model.create_task_subtask_response import CreateTaskSubtaskResponse
from ..model.list_task_subtask_request import ListTaskSubtaskRequest
from ..model.list_task_subtask_response import ListTaskSubtaskResponse


class TaskSubtask(object):
    def __init__(self, config: Config) -> None:
        self.config: Optional[Config] = config

    def create(self, request: CreateTaskSubtaskRequest,
               option: Optional[RequestOption] = None) -> CreateTaskSubtaskResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: CreateTaskSubtaskResponse = JSON.unmarshal(str(resp.content, UTF_8), CreateTaskSubtaskResponse)
        response.raw = resp

        return response

    def list(self, request: ListTaskSubtaskRequest, option: Optional[RequestOption] = None) -> ListTaskSubtaskResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: ListTaskSubtaskResponse = JSON.unmarshal(str(resp.content, UTF_8), ListTaskSubtaskResponse)
        response.raw = resp

        return response
