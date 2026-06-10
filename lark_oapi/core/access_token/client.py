import json
from typing import Dict, Optional

from lark_oapi.core.client_assertion import build_proxy_url, resolve_oauth_aud, resolve_oauth_base_url
from lark_oapi.core.const import (
    APPLICATION_JSON,
    CLIENT_ASSERTION_TYPE_JWT_BEARER,
    CONTENT_TYPE,
    ERR_CODE_APP_SECRET_AND_CLIENT_ASSERTION_EMPTY,
    ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED,
    ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY,
    GRANT_TYPE_AUTHORIZATION_CODE,
    GRANT_TYPE_REFRESH_TOKEN,
    OAUTH_TOKEN_URI,
    UTF_8,
    X_TARGET_SERVICE,
)
from lark_oapi.core.enum import HttpMethod
from lark_oapi.core.exception import AccessTokenException, ClientAssertionException
from lark_oapi.core.http import Transport
from lark_oapi.core.model import BaseRequest, Config, RequestOption
from lark_oapi.core.utils import Strings
from .model import AccessTokenResponse, value_if_not_empty


class AccessToken(object):
    def __init__(self, config: Config) -> None:
        self._config = config

    def retrieve_by_authorization_code(
            self,
            code: str,
            redirect_uri: Optional[str] = None,
            code_verifier: Optional[str] = None,
            scope: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
    ) -> AccessTokenResponse:
        return self._do_request(
            {
                "grant_type": GRANT_TYPE_AUTHORIZATION_CODE,
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
                "scope": scope,
            },
            headers=headers,
        )

    def refresh(
            self,
            refresh_token: str,
            scope: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None,
    ) -> AccessTokenResponse:
        return self._do_request(
            {
                "grant_type": GRANT_TYPE_REFRESH_TOKEN,
                "refresh_token": refresh_token,
                "scope": scope,
            },
            headers=headers,
        )

    def _do_request(self, body: Dict[str, object], headers: Optional[Dict[str, str]] = None) -> AccessTokenResponse:
        oauth_base_url = resolve_oauth_base_url(self._config)
        aud = resolve_oauth_aud(self._config)
        request_url = oauth_base_url + OAUTH_TOKEN_URI
        body = {k: v for k, v in body.items() if v is not None}
        body["client_id"] = self._config.app_id
        option = RequestOption()
        if headers:
            option.headers.update(headers)

        if self._config.client_assertion_provider is not None:
            try:
                assertion_token = self._config.client_assertion_provider.retrieve_token(aud)
            except Exception as e:
                raise ClientAssertionException(ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED, str(e))
            if assertion_token is None or Strings.is_empty(assertion_token.value):
                raise ClientAssertionException(ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY, "client assertion token is empty")
            body["client_assertion_type"] = CLIENT_ASSERTION_TYPE_JWT_BEARER
            body["client_assertion"] = assertion_token.value
            if assertion_token.target_info is not None:
                request_url = build_proxy_url(assertion_token.target_info, OAUTH_TOKEN_URI)
                option.headers[X_TARGET_SERVICE] = aud
        elif Strings.is_not_empty(self._config.app_secret):
            body["client_secret"] = self._config.app_secret
        else:
            raise ClientAssertionException(
                ERR_CODE_APP_SECRET_AND_CLIENT_ASSERTION_EMPTY,
                "AppSecret and ClientAssertionProvider cannot both be empty for AccessToken APIs",
            )

        req = BaseRequest()
        req.http_method = HttpMethod.POST
        req.uri = request_url
        req.headers = {CONTENT_TYPE: APPLICATION_JSON}
        req.body = body
        raw = Transport.execute(self._config, req, option)
        resp = json.loads(str(raw.content, UTF_8))
        if raw.status_code != 200 or _is_error_response(resp):
            raise AccessTokenException(
                raw.status_code,
                resp.get("code") or 0,
                resp.get("error") or resp.get("msg") or "",
                resp.get("error_description") or resp.get("msg") or "",
            )
        access_token = value_if_not_empty(resp.get("access_token"))
        if access_token is None:
            raise AccessTokenException(
                raw.status_code,
                resp.get("code") or 0,
                resp.get("error") or "",
                resp.get("error_description") or "oauth token response missing access_token",
            )
        return AccessTokenResponse(
            access_token=access_token,
            token_type=value_if_not_empty(resp.get("token_type")),
            expires_in=value_if_not_empty(resp.get("expires_in")),
            refresh_token=value_if_not_empty(resp.get("refresh_token")),
            refresh_token_expires_in=value_if_not_empty(resp.get("refresh_token_expires_in")),
            scope=value_if_not_empty(resp.get("scope")),
            raw=raw,
        )


def _is_error_response(resp: Dict[str, object]) -> bool:
    if resp.get("error"):
        return True
    code = resp.get("code")
    return code not in (None, "", 0, "0")
