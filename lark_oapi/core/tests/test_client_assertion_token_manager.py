import json
from types import SimpleNamespace

import pytest

from lark_oapi.core.client_assertion import ClientAssertionToken, TargetInfo
from lark_oapi.core.exception import ClientAssertionException
from lark_oapi.core.model import Config
from lark_oapi.core.enum import AppType
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


def test_isv_assertion_tenant_exchange_and_cache(monkeypatch):
    provider = RecordingProvider()
    config = _config(provider)
    config.app_type = AppType.ISV
    config.app_secret = "unused-secret"
    cache = DictCache()
    monkeypatch.setattr(TokenManager, "cache", cache)
    requests = []

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        body = json.loads(data.decode())
        requests.append(body)
        assert url == "https://accounts.feishu.cn/oauth/v3/token"
        assert headers["Content-Type"] == "application/json"
        return _response({"access_token": "token-" + body["tenant_key"], "expires_in": 7200, "token_type": "Bearer"})

    import lark_oapi.core.http.transport as transport
    monkeypatch.setattr(transport.requests, "request", fake_request)
    for tenant in ["tenant-A", "tenant-B", "tenant-A", "tenant-B"]:
        assert TokenManager.get_isv_tenant_token(config, tenant, "") == "token-" + tenant
    assert len(requests) == 2
    assert requests[0] == {
        "grant_type": "client_credentials", "client_id": "cli_a",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": "client-assertion", "tenant_key": "tenant-A",
    }
    assert len(provider.calls) == 2
    assert len(cache.data) == 2


@pytest.mark.parametrize("failure,status,message", [
    ({"code": 400, "error_description": "assertion rejected", "error": "invalid_client"}, 200, "ISV tenant token exchange failed (HTTP 200), error: invalid_client, error_description: assertion rejected"),
    ({"code": 400, "error_description": "assertion rejected"}, 200, "ISV tenant token exchange failed (HTTP 200), error_description: assertion rejected"),
    ({"code": 400}, 200, "ISV tenant token exchange failed (HTTP 200)"),
    ({"error": "invalid_client"}, 200, "ISV tenant token exchange failed (HTTP 200), error: invalid_client"),
    ({"error": "invalid_client", "error_description": "assertion rejected", "code": 400}, 400, "ISV tenant token exchange failed (HTTP 400), error: invalid_client, error_description: assertion rejected"),
    ({}, 400, "ISV tenant token exchange failed (HTTP 400)"),
    ({"access_token": ""}, 200, "access_token is empty"),
    ({"expires_in": 0}, 200, "expires_in must be positive"),
    ({"token_type": "Other"}, 200, "token_type must be Bearer"),
])
def test_isv_rejects_failed_responses_without_caching(monkeypatch, caplog, failure, status, message):
    config = _config(RecordingProvider())
    config.app_type = AppType.ISV
    cache = DictCache()
    monkeypatch.setattr(TokenManager, "cache", cache)
    import lark_oapi.core.http.transport as transport
    monkeypatch.setattr(transport.requests, "request", lambda *args, **kwargs: _response({
        "access_token": "test-token", "expires_in": 7200, "token_type": "Bearer", **failure,
    }, status))
    with pytest.raises(ClientAssertionException) as exc:
        TokenManager.get_isv_tenant_token(config, "tenant-A", "")
    assert message in exc.value.msg
    is_exchange_error = status != 200 or failure.get("code", 0) != 0 or failure.get("error")
    assert exc.value.code == (failure.get("code") or status if is_exchange_error else 0)
    assert message in caplog.text
    assert "client-assertion" not in caplog.text
    assert "test-token" not in caplog.text
    assert cache.data == {}


def test_isv_proxy_and_endpoint_cache_isolation(monkeypatch):
    config = _config(RecordingProvider(ClientAssertionToken("client-assertion", TargetInfo("proxy.example.com", "/proxy"))))
    config.app_type = AppType.ISV
    cache = DictCache()
    monkeypatch.setattr(TokenManager, "cache", cache)
    calls = []
    def fake_request(method, url, headers=None, **kwargs):
        calls.append(url)
        assert headers["X-Target-Service"] == "accounts.feishu.cn"
        return _response({"access_token": "test-token", "expires_in": 7200, "token_type": "Bearer"})
    import lark_oapi.core.http.transport as transport
    monkeypatch.setattr(transport.requests, "request", fake_request)
    for prefix in ["/region-A", "/region-B", "/region-A"]:
        config.oauth_base_url = "https://accounts.feishu.cn" + prefix
        assert TokenManager.get_isv_tenant_token(config, "tenant-A", "") == "test-token"
    assert calls == ["https://proxy.example.com/proxy/oauth/v3/token"] * 2


def test_isv_cache_write_failure_keeps_existing_behavior(monkeypatch):
    config = _config(RecordingProvider())
    config.app_type = AppType.ISV
    cache = DictCache()
    failure = RuntimeError("cache unavailable")
    def fail_set(*args):
        raise failure
    monkeypatch.setattr(cache, "set", fail_set)
    monkeypatch.setattr(TokenManager, "cache", cache)
    import lark_oapi.core.http.transport as transport
    monkeypatch.setattr(transport.requests, "request", lambda *args, **kwargs: _response({
        "access_token": "test-token", "expires_in": 7200, "token_type": "Bearer",
    }))
    with pytest.raises(RuntimeError) as caught:
        TokenManager.get_isv_tenant_token(config, "tenant-A", "")
    assert caught.value is failure


def test_isv_short_lifetime_keeps_existing_cache_write(monkeypatch):
    import time
    import lark_oapi.core.http.transport as transport
    config = _config(RecordingProvider())
    config.app_type = AppType.ISV
    cache = DictCache()
    monkeypatch.setattr(TokenManager, "cache", cache)
    monkeypatch.setattr(transport.requests, "request", lambda *args, **kwargs: _response({
        "access_token": "test-token", "expires_in": 60, "token_type": "Bearer",
    }))
    before = int(time.time())
    assert TokenManager.get_isv_tenant_token(config, "tenant-A", "") == "test-token"
    assert len(cache.data) == 1
    assert before <= next(iter(cache.expires.values())) <= int(time.time())
