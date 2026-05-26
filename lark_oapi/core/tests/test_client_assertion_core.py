import pytest

from lark_oapi.core.const import (
    CLIENT_ASSERTION_TYPE_JWT_BEARER,
    ERR_CODE_APP_SECRET_AND_CLIENT_ASSERTION_EMPTY,
    ERR_CODE_CLIENT_ASSERTION_MODE_NOT_SUPPORTED,
    ERR_CODE_CLIENT_ASSERTION_PROVIDER_NOT_CONFIGURED,
    ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED,
    ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY,
    FEISHU_OAUTH_DOMAIN,
    GRANT_TYPE_JWT_BEARER,
    LARK_OAUTH_DOMAIN,
    OAUTH_TOKEN_URI,
    X_TARGET_SERVICE,
)
from lark_oapi.core.client_assertion import (
    TargetInfo,
    build_proxy_url,
    resolve_oauth_aud,
    resolve_oauth_base_url,
)
from lark_oapi.core.model import Config


def test_client_assertion_constants_match_go_sdk():
    assert FEISHU_OAUTH_DOMAIN == "https://accounts.feishu.cn"
    assert LARK_OAUTH_DOMAIN == "https://accounts.larksuite.com"
    assert OAUTH_TOKEN_URI == "/oauth/v3/token"
    assert GRANT_TYPE_JWT_BEARER == "urn:ietf:params:oauth:grant-type:jwt-bearer"
    assert CLIENT_ASSERTION_TYPE_JWT_BEARER == "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    assert X_TARGET_SERVICE == "X-Target-Service"
    assert ERR_CODE_CLIENT_ASSERTION_PROVIDER_NOT_CONFIGURED == 7100
    assert ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY == 7101
    assert ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED == 7102
    assert ERR_CODE_CLIENT_ASSERTION_MODE_NOT_SUPPORTED == 7103
    assert ERR_CODE_APP_SECRET_AND_CLIENT_ASSERTION_EMPTY == 7104


def test_resolve_oauth_base_url_default_feishu():
    config = Config()
    config.domain = "https://open.feishu.cn"

    assert resolve_oauth_base_url(config) == "https://accounts.feishu.cn"
    assert resolve_oauth_aud(config) == "accounts.feishu.cn"


def test_resolve_oauth_base_url_default_lark():
    config = Config()
    config.domain = "https://open.larksuite.com"

    assert resolve_oauth_base_url(config) == "https://accounts.larksuite.com"
    assert resolve_oauth_aud(config) == "accounts.larksuite.com"


def test_resolve_oauth_base_url_explicit_localhost():
    config = Config()
    config.oauth_base_url = "http://127.0.0.1:18080/"

    assert resolve_oauth_base_url(config) == "http://127.0.0.1:18080"
    assert resolve_oauth_aud(config) == "127.0.0.1:18080"


def test_resolve_oauth_base_url_requires_explicit_for_custom_domain():
    config = Config()
    config.domain = "https://open.feishu-boe.cn"

    with pytest.raises(ValueError, match="OAuthBaseUrl is not configured"):
        resolve_oauth_base_url(config)


def test_build_proxy_url_adds_https_when_scheme_missing():
    target_info = TargetInfo(target_service="proxy.example.com", target_prefix="/proxy")

    assert build_proxy_url(target_info, "/oauth/v3/token") == "https://proxy.example.com/proxy/oauth/v3/token"
