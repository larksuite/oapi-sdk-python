# Code generated by Lark OpenAPI.

import io
from typing import Any, Optional, Union, Dict, List, Set, IO, Callable, Type
from lark_oapi.core.const import UTF_8, CONTENT_TYPE, APPLICATION_JSON
from lark_oapi.core import JSON
from lark_oapi.core.token import verify
from lark_oapi.core.http import Transport
from lark_oapi.core.model import Config, RequestOption, RawResponse
from lark_oapi.core.utils import Files
from requests_toolbelt import MultipartEncoder
from ..model.query_job_grade_request import QueryJobGradeRequest
from ..model.query_job_grade_response import QueryJobGradeResponse


class JobGrade(object):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    def query(self, request: QueryJobGradeRequest, option: Optional[RequestOption] = None) -> QueryJobGradeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 添加 content-type
        if request.body is not None:
            option.headers[CONTENT_TYPE] = f"{APPLICATION_JSON}; charset=utf-8"

        # 发起请求
        resp: RawResponse = Transport.execute(self.config, request, option)

        # 反序列化
        response: QueryJobGradeResponse = JSON.unmarshal(str(resp.content, UTF_8), QueryJobGradeResponse)
        response.raw = resp

        return response

    async def aquery(self, request: QueryJobGradeRequest,
                     option: Optional[RequestOption] = None) -> QueryJobGradeResponse:
        if option is None:
            option = RequestOption()

        # 鉴权、获取 token
        verify(self.config, request, option)

        # 发起请求
        resp: RawResponse = await Transport.aexecute(self.config, request, option)

        # 反序列化
        response: QueryJobGradeResponse = JSON.unmarshal(str(resp.content, UTF_8), QueryJobGradeResponse)
        response.raw = resp

        return response