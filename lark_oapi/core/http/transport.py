import requests
from requests_toolbelt import MultipartEncoder

from lark_oapi.core.const import *
from lark_oapi.core.json import JSON
from lark_oapi.core.log import logger
from lark_oapi.core.model import *


class Transport(object):

    @staticmethod
    def execute(conf: Config, req: BaseRequest, option: Optional[RequestOption] = None) -> RawResponse:
        if option is None:
            option = RequestOption()

        # 拼接url
        url: str = _build_url(conf.domain, req.uri, req.paths)

        # 组装header
        headers: Dict[str, str] = _build_header(req, option)

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

        logger.debug(f"{str(req.http_method.name)} {url} {response.status_code}, "
                     f"headers: {JSON.marshal(headers)}, "
                     f"params: {JSON.marshal(req.queries)}, "
                     f"body: {str(data, UTF_8) if isinstance(data, bytes) else data}")

        resp = RawResponse()
        resp.status_code = response.status_code
        resp.headers = dict(response.headers)
        resp.content = response.content

        return resp


def _build_url(domain: str, uri: str, paths: Dict[str, str]) -> str:
    if paths is None:
        paths = {}
    for key in paths:
        uri = uri.replace(":" + key, paths[key])

    return domain + uri


def _build_header(request: BaseRequest, option: RequestOption) -> Dict[str, str]:
    headers = request.headers

    # 添加ua
    headers[USER_AGENT] = f"{PROJECT}/v{VERSION}"

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
