import json
from types import SimpleNamespace

import pytest

from lark_oapi import Client
from lark_oapi.core.client_assertion import ClientAssertionToken, TargetInfo
from lark_oapi.core.exception import AccessTokenException, ClientAssertionException


class RecordingProvider:
    def __init__(self, token=None):
        self.token = token or ClientAssertionToken("client-assertion")
        self.calls = []

    def retrieve_token(self, aud):
        self.calls.append(aud)
        return self.token


def _response(payload, status=200):
    return SimpleNamespace(status_code=status, headers={"Content-Type": "application/json"}, content=json.dumps(payload).encode())


def _client(provider=None, app_secret="", oauth_base_url="https://accounts.feishu.cn"):
    builder = Client.builder().app_id("cli_a").oauth_base_url(oauth_base_url)
    if provider is not None:
        builder.client_assertion_provider(provider)
    if app_secret:
        builder.app_secret(app_secret)
    return builder.build()


def test_access_token_authorization_code_with_client_assertion(monkeypatch):
    provider = RecordingProvider()
    client = _client(provider)
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["url"] = url
        captured["body"] = json.loads(data.decode())
        return _response({"access_token": "user-token", "token_type": "Bearer", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    resp = client.access_token.retrieve_by_authorization_code(
        code="code",
        redirect_uri="https://example.com/cb",
        code_verifier="verifier",
    )

    assert resp.access_token == "user-token"
    assert captured["url"] == "https://accounts.feishu.cn/oauth/v3/token"
    assert captured["body"]["grant_type"] == "authorization_code"
    assert captured["body"]["client_id"] == "cli_a"
    assert captured["body"]["client_assertion"] == "client-assertion"
    assert captured["body"]["client_assertion_type"] == "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    assert captured["body"]["code"] == "code"
    assert captured["body"]["redirect_uri"] == "https://example.com/cb"
    assert captured["body"]["code_verifier"] == "verifier"
    assert provider.calls == ["accounts.feishu.cn"]


def test_access_token_refresh_with_client_assertion(monkeypatch):
    client = _client(RecordingProvider())
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["body"] = json.loads(data.decode())
        return _response({"access_token": "user-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    assert client.access_token.refresh(refresh_token="refresh-token").access_token == "user-token"
    assert captured["body"]["grant_type"] == "refresh_token"
    assert captured["body"]["refresh_token"] == "refresh-token"
    assert captured["body"]["client_assertion"] == "client-assertion"


def test_access_token_authorization_code_with_app_secret_fallback(monkeypatch):
    client = _client(provider=None, app_secret="app-secret")
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["body"] = json.loads(data.decode())
        return _response({"access_token": "user-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    client.access_token.retrieve_by_authorization_code(code="code")

    assert captured["body"]["client_secret"] == "app-secret"
    assert "client_assertion" not in captured["body"]
    assert "client_assertion_type" not in captured["body"]


def test_access_token_refresh_with_app_secret_fallback(monkeypatch):
    client = _client(provider=None, app_secret="app-secret")
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["body"] = json.loads(data.decode())
        return _response({"access_token": "user-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    client.access_token.refresh(refresh_token="refresh-token")

    assert captured["body"]["client_secret"] == "app-secret"
    assert captured["body"]["refresh_token"] == "refresh-token"


def test_access_token_rejects_missing_credentials():
    client = _client(provider=None, app_secret="")

    with pytest.raises(ClientAssertionException) as err:
        client.access_token.retrieve_by_authorization_code(code="code")

    assert err.value.code == 7104


def test_access_token_returns_access_token_exception_for_non_200(monkeypatch):
    client = _client(RecordingProvider())

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        return _response({
            "code": 20001,
            "error": "invalid_client",
            "error_description": "client assertion invalid",
        }, status=401)

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    with pytest.raises(AccessTokenException) as err:
        client.access_token.retrieve_by_authorization_code(code="code")

    assert err.value.status_code == 401
    assert err.value.code == 20001
    assert err.value.error == "invalid_client"
    assert err.value.error_description == "client assertion invalid"


def test_access_token_rejects_200_error_payload(monkeypatch):
    client = _client(RecordingProvider())

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        return _response({
            "code": 20138,
            "msg": "authorization code is invalid",
        })

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    with pytest.raises(AccessTokenException) as err:
        client.access_token.retrieve_by_authorization_code(code="bad-code")

    assert err.value.status_code == 200
    assert err.value.code == 20138
    assert err.value.error_description == "authorization code is invalid"


def test_access_token_rejects_200_without_access_token(monkeypatch):
    client = _client(RecordingProvider())

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        return _response({"token_type": "Bearer", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    with pytest.raises(AccessTokenException) as err:
        client.access_token.retrieve_by_authorization_code(code="code")

    assert err.value.status_code == 200
    assert err.value.code == 0
    assert err.value.error_description == "oauth token response missing access_token"


def test_access_token_proxy_keeps_custom_headers(monkeypatch):
    provider = RecordingProvider(
        ClientAssertionToken(
            "client-assertion",
            TargetInfo(target_service="proxy.example.com", target_prefix="/proxy"),
        )
    )
    client = _client(provider)
    captured = {}

    def fake_request(method, url, headers=None, params=None, data=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        return _response({"access_token": "user-token", "expires_in": 7200})

    import lark_oapi.core.http.transport as transport

    monkeypatch.setattr(transport.requests, "request", fake_request)

    client.access_token.retrieve_by_authorization_code(
        code="code",
        headers={"X-Custom": "custom-value"},
    )

    assert captured["url"] == "https://proxy.example.com/proxy/oauth/v3/token"
    assert captured["headers"]["X-Custom"] == "custom-value"
    assert captured["headers"]["X-Target-Service"] == "accounts.feishu.cn"
