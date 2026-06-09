import json
import urllib.parse
from typing import Any, Optional

import httpx
import requests
from requests_toolbelt import MultipartEncoder

from lark_oapi.core.const import *
from lark_oapi.core.json import JSON
from lark_oapi.core.log import logger
from lark_oapi.core.model import *
from lark_oapi.core.utils.user_agent import build_user_agent


_REDACTED = "***"
_SENSITIVE_KEYWORDS = ("authorization", "token", "secret", "assertion", "password", "ticket")


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

        logger.debug(f"{str(req.http_method.name)} {_redact_url(url)} {response.status_code}, "
                     f"headers: {_marshal_log_value(headers)}, "
                     f"params: {_marshal_log_value(req.queries)}, "
                     f"body: {_marshal_log_body(data)}")

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
                f"{str(req.http_method.name)} {_redact_url(url)} {response.status_code}"
                f"{f', headers: {_marshal_log_value(headers)}' if headers else ''}"
                f"{f', params: {_marshal_log_value(req.queries)}' if req.queries else ''}"
                f"{f', body: {_marshal_log_value(_merge_dicts(json_, files, data))}' if json_ or files or data else ''}"
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


def _is_sensitive_key(key: Any) -> bool:
    key = str(key).lower()
    return any(keyword in key for keyword in _SENSITIVE_KEYWORDS)


def _redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _REDACTED if _is_sensitive_key(key) else _redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        if len(value) == 2 and not isinstance(value[0], (dict, list, tuple)) and _is_sensitive_key(value[0]):
            return value[0], _REDACTED
        return tuple(_redact_sensitive(item) for item in value)
    if isinstance(value, list):
        if len(value) == 2 and not isinstance(value[0], (dict, list, tuple)) and _is_sensitive_key(value[0]):
            return [value[0], _REDACTED]
        return [_redact_sensitive(item) for item in value]
    return value


def _marshal_log_value(value: Any) -> Optional[str]:
    return JSON.marshal(_redact_sensitive(value))


def _marshal_log_body(data: Any) -> str:
    if data is None:
        return "None"
    if isinstance(data, MultipartEncoder):
        return _REDACTED
    if isinstance(data, bytes):
        try:
            return _marshal_log_value(json.loads(str(data, UTF_8)))
        except Exception:
            return _REDACTED
    value = _marshal_log_value(data)
    return value if value is not None else "None"


def _redact_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if not parsed.query:
        return url

    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    redacted_query = [
        (key, _REDACTED if _is_sensitive_key(key) else value)
        for key, value in query
    ]
    return urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        urllib.parse.urlencode(redacted_query),
        parsed.fragment,
    ))


def _merge_dicts(*dicts):
    res = {}
    for d in dicts:
        if d is not None:
            res.update(d)
    return res
