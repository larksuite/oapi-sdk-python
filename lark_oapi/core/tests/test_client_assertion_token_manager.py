import json
from types import SimpleNamespace

import pytest

from lark_oapi.core.client_assertion import ClientAssertionToken, TargetInfo
from lark_oapi.core.exception import ClientAssertionException
from lark_oapi.core.model import Config
from lark_oapi.core.token import TokenManager


class DictCache:
    def __init__(self):
        self.data = {}
        self.expires = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, expire):
        self.data[key] = value
        self.expires[key] = expire


_DEFAULT = object()


class RecordingProvider:
    def __init__(self, token=_DEFAULT, err=None):
        self.token = ClientAssertionToken("client-assertion") if token is _DEFAULT else token
        self.err = err
        self.calls = []

    def retrieve_token(self, aud):
        self.calls.append(aud)
        if self.err:
            raise self.err
        return self.token


def _config(provider):
    config = Config()
    config.app_id = "cli_a"
    config.app_secret = ""
    config.domain = "https://open.feishu.cn"
    config.oauth_base_url = "https://accounts.feishu.cn"
    config.client_assertion_provider = provider
    return config


def _response(payload, status=200):
    return SimpleNamespace(status_code=status, headers={"Content-Type": "application/json"}, content=json.dumps(payload).encode())


def _client_assertion_cache_key(aud="accounts.feishu.cn"):
    return f"self_tenant_token:client_assertion:cli_a:{aud}"


def test_get_self_tenant_token_by_client_assertion_requests_oauth_token(monkeypatch):
    provider = RecordingProvider()
    config = _config(provider)
    cache = DictCache()
    monkeypatch.setattr(TokenManager, "cache", cache)
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["body"] = json.loads(data.decode())
        return _response({"access_token": "tenant-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    token = TokenManager.get_self_tenant_token(config)

    assert token == "tenant-token"
    assert captured["url"] == "https://accounts.feishu.cn/oauth/v3/token"
    assert captured["body"] == {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": "client-assertion",
        "client_id": "cli_a",
    }
    assert provider.calls == ["accounts.feishu.cn"]
    assert cache.data[_client_assertion_cache_key()] == "tenant-token"


def test_get_self_tenant_token_by_client_assertion_cache_hit_skips_provider(monkeypatch):
    provider = RecordingProvider()
    config = _config(provider)
    cache = DictCache()
    cache.data[_client_assertion_cache_key()] = "cached-token"
    monkeypatch.setattr(TokenManager, "cache", cache)

    assert TokenManager.get_self_tenant_token(config) == "cached-token"
    assert provider.calls == []


def test_client_assertion_tenant_token_cache_does_not_reuse_app_secret_entry(monkeypatch):
    provider = RecordingProvider()
    config = _config(provider)
    cache = DictCache()
    cache.data["self_tenant_token:cli_a"] = "cached-appsecret-token"
    monkeypatch.setattr(TokenManager, "cache", cache)

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        return _response({"access_token": "tenant-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    assert TokenManager.get_self_tenant_token(config) == "tenant-token"
    assert provider.calls == ["accounts.feishu.cn"]
    assert cache.data[_client_assertion_cache_key()] == "tenant-token"


def test_get_self_tenant_token_by_client_assertion_with_proxy(monkeypatch):
    provider = RecordingProvider(
        ClientAssertionToken(
            "client-assertion",
            TargetInfo(target_service="proxy.example.com", target_prefix="/proxy"),
        )
    )
    config = _config(provider)
    cache = DictCache()
    monkeypatch.setattr(TokenManager, "cache", cache)
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        return _response({"access_token": "tenant-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    assert TokenManager.get_self_tenant_token(config) == "tenant-token"
    assert captured["url"] == "https://proxy.example.com/proxy/oauth/v3/token"
    assert captured["headers"]["X-Target-Service"] == "accounts.feishu.cn"


@pytest.mark.parametrize("token", [None, ClientAssertionToken("")])
def test_get_self_tenant_token_by_client_assertion_empty_token(monkeypatch, token):
    config = _config(RecordingProvider(token=token))
    monkeypatch.setattr(TokenManager, "cache", DictCache())

    with pytest.raises(ClientAssertionException) as err:
        TokenManager.get_self_tenant_token(config)

    assert err.value.code == 7101


def test_get_self_tenant_token_by_client_assertion_provider_error(monkeypatch):
    config = _config(RecordingProvider(err=RuntimeError("boom")))
    monkeypatch.setattr(TokenManager, "cache", DictCache())

    with pytest.raises(ClientAssertionException) as err:
        TokenManager.get_self_tenant_token(config)

    assert err.value.code == 7102
    assert "boom" in err.value.msg


def test_get_self_tenant_token_by_client_assertion_oauth_error_message_priority(monkeypatch):
    config = _config(RecordingProvider())
    monkeypatch.setattr(TokenManager, "cache", DictCache())

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        return _response({
            "code": 20001,
            "error": "invalid_client",
            "error_description": "client assertion invalid",
        })

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    with pytest.raises(ClientAssertionException) as err:
        TokenManager.get_self_tenant_token(config)

    assert err.value.code == 20001
    assert err.value.msg == "client assertion invalid"


def test_get_self_app_token_blocked_in_client_assertion_mode():
    config = _config(RecordingProvider())

    with pytest.raises(ClientAssertionException) as err:
        TokenManager.get_self_app_token(config)

    assert err.value.code == 7100
