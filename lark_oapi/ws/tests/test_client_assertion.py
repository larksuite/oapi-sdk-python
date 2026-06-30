from types import SimpleNamespace

import pytest

from lark_oapi.core.client_assertion import ClientAssertionToken, TargetInfo
from lark_oapi.ws import client as ws_client
from lark_oapi.ws.exception import ClientException, ServerException


class RecordingProvider:
    def __init__(self, tokens=None, err=None):
        self.tokens = list(tokens or [ClientAssertionToken("assertion")])
        self.err = err
        self.calls = []

    def retrieve_token(self, aud):
        self.calls.append(aud)
        if self.err:
            raise self.err
        if len(self.tokens) == 1:
            return self.tokens[0]
        return self.tokens.pop(0)


def _ok_response():
    return SimpleNamespace(
        status_code=200,
        content=b'{"code":0,"data":{"URL":"ws://example.test/callback?device_id=device&service_id=42"}}',
    )


def test_ws_get_conn_url_with_app_secret_keeps_existing_behavior(monkeypatch):
    captured = {}

    def fake_post(url, *, headers=None, json=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _ok_response()

    monkeypatch.setattr(ws_client.requests, "post", fake_post)
    client = ws_client.Client("app_id", "app_secret")

    assert client._get_conn_url() == "ws://example.test/callback?device_id=device&service_id=42"
    assert captured["json"] == {"AppID": "app_id", "AppSecret": "app_secret"}


def test_ws_get_conn_url_with_client_assertion(monkeypatch):
    captured = {}
    provider = RecordingProvider()

    def fake_post(url, *, headers=None, json=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _ok_response()

    monkeypatch.setattr(ws_client.requests, "post", fake_post)
    client = ws_client.Client("app_id", "", client_assertion_provider=provider)

    assert client._get_conn_url() == "ws://example.test/callback?device_id=device&service_id=42"
    assert captured["json"] == {"AppID": "app_id", "AppSecret": "", "ClientAssertion": "assertion"}
    assert provider.calls == ["open.feishu.cn"]


def test_ws_get_conn_url_with_client_assertion_proxy(monkeypatch):
    captured = {}
    provider = RecordingProvider([
        ClientAssertionToken(
            "assertion",
            TargetInfo(target_service="proxy.example.com", target_prefix="/proxy"),
        )
    ])

    def fake_post(url, *, headers=None, json=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _ok_response()

    monkeypatch.setattr(ws_client.requests, "post", fake_post)
    client = ws_client.Client(
        "app_id",
        "",
        domain="https://open.feishu.cn",
        headers={"X-Target-Service": "caller-value", "X-Custom": "custom-value"},
        client_assertion_provider=provider,
    )

    client._get_conn_url()

    assert captured["url"] == "https://proxy.example.com/proxy/callback/ws/endpoint"
    assert captured["headers"]["X-Target-Service"] == "open.feishu.cn"
    assert captured["headers"]["X-Custom"] == "custom-value"
    assert captured["json"] == {"AppID": "app_id", "AppSecret": "", "ClientAssertion": "assertion"}


def test_ws_get_conn_url_retrieves_token_each_time(monkeypatch):
    assertions = []
    provider = RecordingProvider([
        ClientAssertionToken("assertion-1"),
        ClientAssertionToken("assertion-2"),
    ])

    def fake_post(url, *, headers=None, json=None):
        assertions.append(json["ClientAssertion"])
        return _ok_response()

    monkeypatch.setattr(ws_client.requests, "post", fake_post)
    client = ws_client.Client("app_id", "", client_assertion_provider=provider)

    client._get_conn_url()
    client._get_conn_url()

    assert assertions == ["assertion-1", "assertion-2"]
    assert provider.calls == ["open.feishu.cn", "open.feishu.cn"]


def test_ws_get_conn_url_empty_client_assertion_token():
    provider = RecordingProvider([ClientAssertionToken("")])
    client = ws_client.Client("app_id", "", client_assertion_provider=provider)

    with pytest.raises(ClientException) as err:
        client._get_conn_url()

    assert err.value.code == 7101


def test_ws_get_conn_url_missing_credentials_message():
    client = ws_client.Client("app_id", "")

    with pytest.raises(ClientException) as err:
        client._get_conn_url()

    assert str(err.value) == (
        "1000040344: app_id is required and either app_secret or client_assertion_provider is required"
    )


def test_ws_provider_error_is_not_wrapped():
    err = RuntimeError("boom")
    provider = RecordingProvider(err=err)
    client = ws_client.Client("app_id", "", client_assertion_provider=provider)

    with pytest.raises(RuntimeError) as raised:
        client._get_conn_url()

    assert raised.value is err


def test_ws_non_200_uses_server_msg_when_available(monkeypatch):
    provider = RecordingProvider()

    def fake_post(url, *, headers=None, json=None):
        return SimpleNamespace(
            status_code=500,
            content=b'{"code":20050,"msg":"target service unavailable"}',
        )

    monkeypatch.setattr(ws_client.requests, "post", fake_post)
    client = ws_client.Client("app_id", "", client_assertion_provider=provider)

    with pytest.raises(ServerException) as err:
        client._get_conn_url()

    assert err.value.code == 500
    assert str(err.value) == "500: target service unavailable"
