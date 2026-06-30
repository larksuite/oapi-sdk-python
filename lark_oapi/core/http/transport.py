import json
import urllib.parse
from typing import Optional

import httpx
import requests
from requests_toolbelt import MultipartEncoder

from lark_oapi.core.const import *
from lark_oapi.core.json import JSON
from lark_oapi.core.log import logger
from lark_oapi.core.model import *
from lark_oapi.core.utils.user_agent import build_user_agent


class Transport(object):

    @staticmethod
    def execute(conf: Config, req: BaseRequest, option: Optional[RequestOption] = None) -> RawResponse:
        if option is None:
            option = RequestOption()

        # 拼接url
        url: str = _build_url(conf.domain, req.uri, req.paths)

        # 组装header
        headers: Dict[str, str] = _build_header(req, option, conf)

        data = req.body
        if data is not None and not isinstance(data, MultipartEncoder):
            data = JSON.marshal(req.body).encode(UTF_8)

        response = requests.request(
            str(req.http_method.name),
            url,
            headers=req.headers,
            params=req.queries,
            data=data,
            timeout=conf.timeout,
        )

        logger.debug(
            f"{str(req.http_method.name)} request completed with status {response.status_code}, "
            f"headers_count: {len(headers)}, "
            f"params_count: {len(req.queries)}, "
            f"body_present: {data is not None}"
        )

        resp = RawResponse()
        resp.status_code = response.status_code
        resp.headers = dict(response.headers)
        resp.content = response.content

        return resp

    @staticmethod
    async def aexecute(conf: Config, req: BaseRequest, option: Optional[RequestOption] = None) -> RawResponse:
        if option is None:
            option = RequestOption()

        # 拼接url
        url: str = _build_url(conf.domain, req.uri, req.paths)

        # 组装header
        headers: Dict[str, str] = _build_header(req, option, conf)

        json_, files, data = None, None, None
        if req.files:
            # multipart/form-data
            files = req.files
            if req.body is not None:
                data = json.loads(JSON.marshal(req.body))
        elif req.body is not None:
            # application/json
            json_ = json.loads(JSON.marshal(req.body))

        async with httpx.AsyncClient() as client:
            response = await client.request(
                str(req.http_method.name),
                url,
                headers=req.headers,
                params=req.queries,
                json=json_,
                data=data,
                files=files,
                timeout=conf.timeout,
            )

            logger.debug(
                f"{str(req.http_method.name)} request completed with status {response.status_code}, "
                f"headers_count: {len(headers)}, "
                f"params_count: {len(req.queries)}, "
                f"body_present: {json_ is not None or files is not None or data is not None}"
            )

            resp = RawResponse()
            resp.status_code = response.status_code
            resp.headers = dict(response.headers)
            resp.content = response.content

            return resp


def _build_url(domain: str, uri: str, paths: Dict[str, str]) -> str:
    if paths is None:
        paths = {}
    for key in paths:
        # Path params must be URL-encoded; safe='' prevents '/', '?', '#'
        # from passing through unencoded (path traversal / query injection).
        value = paths[key]
        if value is None:
            value = ""
        encoded = urllib.parse.quote(str(value), safe="")
        uri = uri.replace(":" + key, encoded)

    if uri.startswith("http://") or uri.startswith("https://"):
        return uri
    return domain + uri


def _build_header(request: BaseRequest, option: RequestOption, conf: Optional[Config] = None) -> Dict[str, str]:
    headers = request.headers

    # 添加ua
    source = getattr(conf, "source", None) if conf is not None else None
    extra_tags = getattr(conf, "extra_ua_tags", None) if conf is not None else None
    headers[USER_AGENT] = build_user_agent(source=source, extra_tags=extra_tags)

    # 附加header
    if option.headers is not None:
        for key in option.headers:
            headers[key] = option.headers[key]

    # 添加token
    for token_type in request.token_types:
        if AccessTokenType.TENANT == token_type:
            headers[AUTHORIZATION] = f"Bearer {option.tenant_access_token}"
        elif AccessTokenType.APP == token_type:
            headers[AUTHORIZATION] = f"Bearer {option.app_access_token}"
        elif AccessTokenType.USER == token_type:
            headers[AUTHORIZATION] = f"Bearer {option.user_access_token}"

    return headers
