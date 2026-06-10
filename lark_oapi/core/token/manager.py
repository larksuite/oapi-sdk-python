import json
import time

from lark_oapi.core import JSON, Strings
from lark_oapi.core.cache import *
from lark_oapi.core.client_assertion import build_proxy_url, resolve_oauth_aud, resolve_oauth_base_url
from lark_oapi.core.const import (
    APPLICATION_JSON,
    CLIENT_ASSERTION_TYPE_JWT_BEARER,
    CONTENT_TYPE,
    ERR_CODE_CLIENT_ASSERTION_PROVIDER_NOT_CONFIGURED,
    ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED,
    ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY,
    GRANT_TYPE_JWT_BEARER,
    OAUTH_TOKEN_URI,
    UTF_8,
    X_TARGET_SERVICE,
)
from lark_oapi.core.exception import ClientAssertionException, ObtainAccessTokenException
from lark_oapi.core.http import Transport
from lark_oapi.core.model import BaseRequest, Config, RawResponse, RequestOption
from lark_oapi.core.enum import HttpMethod
from .access_token_response import AccessTokenResponse
from .create_isv_app_token_request import CreateIsvAppTokenRequest
from .create_isv_tenant_token_request import CreateIsvTenantTokenRequest
from .create_self_app_token_request import CreateSelfAppTokenRequest
from .create_self_tenant_token_request import CreateSelfTenantTokenRequest
from .create_token_request_body import CreateTokenRequestBody


class TokenManager(object):
    cache: ICache = LocalCache.instance()

    @staticmethod
    def get_self_app_token(conf: Config) -> str:
        if conf.client_assertion_provider is not None:
            raise ClientAssertionException(
                ERR_CODE_CLIENT_ASSERTION_PROVIDER_NOT_CONFIGURED,
                "AppAccessToken is not available in ClientAssertion mode",
            )

        # 读缓存
        cache_key = f"self_app_token:{conf.app_id}"
        token = TokenManager.cache.get(cache_key)
        if Strings.is_not_empty(token):
            return token

        # 缓存不存在则发起请求获取token
        req: CreateSelfAppTokenRequest = CreateSelfAppTokenRequest.builder() \
            .request_body(CreateTokenRequestBody.builder()
                          .app_id(conf.app_id)
                          .app_secret(conf.app_secret)
                          .build()) \
            .build()
        raw: RawResponse = Transport.execute(conf, req)
        resp = JSON.unmarshal(str(raw.content, UTF_8), AccessTokenResponse)

        if not resp.success():
            raise ObtainAccessTokenException("obtain self app access token failed", resp.code, resp.msg)

        # 写缓存
        token = resp.app_access_token
        expire = time.time() + resp.expire - 10 * 60  # 提前10分钟过期
        TokenManager.cache.set(cache_key, token, int(expire))

        return token

    @staticmethod
    def get_self_tenant_token(config: Config) -> str:
        if config.client_assertion_provider is not None:
            return TokenManager._get_self_tenant_token_by_client_assertion(config)

        # 读缓存
        cache_key = f"self_tenant_token:{config.app_id}"
        token = TokenManager.cache.get(cache_key)
        if Strings.is_not_empty(token):
            return token

        # 缓存不存在则发起请求获取token
        req: CreateSelfTenantTokenRequest = CreateSelfTenantTokenRequest.builder() \
            .request_body(CreateTokenRequestBody.builder()
                          .app_id(config.app_id)
                          .app_secret(config.app_secret)
                          .build()) \
            .build()
        raw: RawResponse = Transport.execute(config, req)
        resp = JSON.unmarshal(str(raw.content, UTF_8), AccessTokenResponse)

        if not resp.success():
            raise ObtainAccessTokenException("obtain self tenant access token failed", resp.code, resp.msg)

        # 写缓存
        token = resp.tenant_access_token
        expire = time.time() + resp.expire - 10 * 60  # 提前10分钟过期
        TokenManager.cache.set(cache_key, token, int(expire))

        return token

    @staticmethod
    def _get_self_tenant_token_by_client_assertion(config: Config) -> str:
        oauth_base_url = resolve_oauth_base_url(config)
        aud = resolve_oauth_aud(config)
        cache_key = f"self_tenant_token:client_assertion:{config.app_id}:{aud}"
        token = TokenManager.cache.get(cache_key)
        if Strings.is_not_empty(token):
            return token

        try:
            assertion_token = config.client_assertion_provider.retrieve_token(aud)
        except Exception as e:
            raise ClientAssertionException(ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED, str(e))
        if assertion_token is None or Strings.is_empty(assertion_token.value):
            raise ClientAssertionException(ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY, "client assertion token is empty")

        req = BaseRequest()
        req.http_method = HttpMethod.POST
        req.uri = oauth_base_url + OAUTH_TOKEN_URI
        req.headers = {CONTENT_TYPE: APPLICATION_JSON}
        req.body = {
            "grant_type": GRANT_TYPE_JWT_BEARER,
            "client_assertion_type": CLIENT_ASSERTION_TYPE_JWT_BEARER,
            "client_assertion": assertion_token.value,
            "client_id": config.app_id,
        }
        option = RequestOption()
        if assertion_token.target_info is not None:
            req.uri = build_proxy_url(assertion_token.target_info, OAUTH_TOKEN_URI)
            option.headers[X_TARGET_SERVICE] = aud

        raw = Transport.execute(config, req, option)
        resp = json.loads(str(raw.content, UTF_8))
        access_token = resp.get("access_token")
        if Strings.is_empty(access_token):
            msg = resp.get("error_description") or resp.get("error") or "oauth token response missing access token"
            raise ClientAssertionException(resp.get("code") or 0, msg)

        expires_in = int(resp.get("expires_in") or 0)
        expire = time.time() + max(expires_in - 180, 0)
        TokenManager.cache.set(cache_key, access_token, int(expire))
        return access_token

    @staticmethod
    def get_isv_app_token(config: Config, app_ticket: str) -> str:
        # 读缓存
        cache_key = f"isv_app_token:{config.app_id}"
        token = TokenManager.cache.get(cache_key)
        if Strings.is_not_empty(token):
            return token

        if Strings.is_empty(app_ticket):
            # TODO: get app ticket from ticket cache
            pass

        # 缓存不存在则发起请求获取token
        req: CreateIsvAppTokenRequest = CreateIsvAppTokenRequest.builder() \
            .request_body(CreateTokenRequestBody.builder()
                          .app_id(config.app_id)
                          .app_secret(config.app_secret)
                          .app_ticket(app_ticket).build()) \
            .build()
        raw: RawResponse = Transport.execute(config, req)
        resp = JSON.unmarshal(str(raw.content, UTF_8), AccessTokenResponse)

        if not resp.success():
            raise ObtainAccessTokenException("obtain isv app access token failed", resp.code, resp.msg)

        # 写缓存
        token = resp.app_access_token
        expire = time.time() + resp.expire - 10 * 60  # 提前10分钟过期
        TokenManager.cache.set(cache_key, token, int(expire))

        return token

    @staticmethod
    def get_isv_tenant_token(config: Config, tenant_key: str, app_ticket: str) -> str:
        # 读缓存
        cache_key = f"isv_tenant_token:{config.app_id}:{tenant_key}"
        token = TokenManager.cache.get(cache_key)
        if Strings.is_not_empty(token):
            return token

        app_token = TokenManager.get_isv_app_token(config, app_ticket)
        # 缓存不存在则发起请求获取token
        req: CreateIsvTenantTokenRequest = CreateIsvTenantTokenRequest.builder() \
            .request_body(CreateTokenRequestBody.builder()
                          .app_access_token(app_token)
                          .tenant_key(tenant_key).build()) \
            .build()
        raw: RawResponse = Transport.execute(config, req)
        resp = JSON.unmarshal(str(raw.content, UTF_8), AccessTokenResponse)

        if not resp.success():
            raise ObtainAccessTokenException("obtain isv tenant access token failed", resp.code, resp.msg)

        # 写缓存
        token = resp.tenant_access_token
        expire = time.time() + resp.expire - 10 * 60  # 提前10分钟过期
        TokenManager.cache.set(cache_key, token, int(expire))

        return token
