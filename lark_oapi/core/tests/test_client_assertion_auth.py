import pytest

from lark_oapi.core import AccessTokenType, AppType
from lark_oapi.core.client_assertion import ClientAssertionToken
from lark_oapi.core.exception import ClientAssertionException, NoAuthorizationException
from lark_oapi.core.model import BaseRequest, Config, RequestOption
from lark_oapi.core.token import TokenManager, verify


class RecordingProvider:
    def __init__(self):
        self.calls = []

    def retrieve_token(self, aud):
        self.calls.append(aud)
        return ClientAssertionToken("assertion")


def _request(*token_types):
    req = BaseRequest()
    req.token_types = set(token_types)
    return req


def _config(provider=None):
    config = Config()
    config.app_id = "cli_a"
    config.app_secret = ""
    config.client_assertion_provider = provider
    return config


def test_verify_client_assertion_prefers_tenant_over_app(monkeypatch):
    provider = RecordingProvider()
    config = _config(provider)
    option = RequestOption()
    req = _request(AccessTokenType.APP, AccessTokenType.TENANT)

    monkeypatch.setattr(TokenManager, "get_self_tenant_token", staticmethod(lambda conf: "tenant-token"))

    verify(config, req, option)

    assert req.token_types == {AccessTokenType.TENANT}
    assert option.tenant_access_token == "tenant-token"


def test_verify_client_assertion_manual_user_token_wins(monkeypatch):
    provider = RecordingProvider()
    config = _config(provider)
    option = RequestOption()
    option.user_access_token = "user-token"
    req = _request(AccessTokenType.TENANT, AccessTokenType.USER)

    def fail_if_called(conf):
        raise AssertionError("tenant token should not be requested")

    monkeypatch.setattr(TokenManager, "get_self_tenant_token", staticmethod(fail_if_called))

    verify(config, req, option)

    assert req.token_types == {AccessTokenType.USER}
    assert provider.calls == []


def test_verify_client_assertion_rejects_app_only():
    config = _config(RecordingProvider())
    req = _request(AccessTokenType.APP)

    with pytest.raises(ClientAssertionException) as err:
        verify(config, req, RequestOption())

    assert err.value.code == 7103


def test_verify_client_assertion_rejects_isv():
    config = _config(RecordingProvider())
    config.app_type = AppType.ISV
    req = _request(AccessTokenType.TENANT)

    with pytest.raises(ClientAssertionException) as err:
        verify(config, req, RequestOption())

    assert err.value.code == 7100


def test_verify_app_secret_mode_still_requires_app_secret():
    config = Config()
    config.app_id = "cli_a"
    config.app_secret = ""
    req = _request(AccessTokenType.TENANT)

    with pytest.raises(NoAuthorizationException) as err:
        verify(config, req, RequestOption())

    assert err.value.msg == "app_id or app_secret not found"
