from types import SimpleNamespace

import pytest

from lark_oapi.core import AccessTokenType, HttpMethod
from lark_oapi.core.http import transport
from lark_oapi.core.json import JSON
from lark_oapi.core.model import BaseRequest, Config, RequestOption


def _request(body):
    req = BaseRequest()
    req.http_method = HttpMethod.POST
    req.uri = "/open-apis/mock"
    req.token_types = {AccessTokenType.TENANT}
    req.body = body
    return req


def test_execute_redacts_sensitive_headers_and_body_from_debug_log(monkeypatch):
    captured = {}
    debug_logs = []
    body = {
        "client_assertion": "assertion-secret",
        "client_secret": "client-secret",
        "nested": {"refresh_token": "refresh-secret"},
        "items": [{"AppSecret": "app-secret"}, {"ClientAssertion": "ws-assertion"}],
    }

    def fake_request(method, url, *, headers=None, params=None, data=None, timeout=None):
        captured["headers"] = dict(headers)
        captured["data"] = data
        return SimpleNamespace(status_code=200, headers={}, content=b"{}")

    monkeypatch.setattr(transport.requests, "request", fake_request)
    monkeypatch.setattr(transport.logger, "debug", lambda msg: debug_logs.append(msg))

    conf = Config()
    req = _request(body)
    option = RequestOption()
    option.tenant_access_token = "tenant-token-secret"
    option.headers = {"X-Api-Token": "header-token-secret"}

    transport.Transport.execute(conf, req, option)

    log_output = "\n".join(debug_logs)
    for secret in (
            "assertion-secret",
            "client-secret",
            "refresh-secret",
            "app-secret",
            "ws-assertion",
            "tenant-token-secret",
            "header-token-secret",
    ):
        assert secret not in log_output
    assert '"Authorization": "***"' in log_output
    assert '"client_assertion": "***"' in log_output

    assert captured["headers"]["Authorization"] == "Bearer tenant-token-secret"
    assert captured["headers"]["X-Api-Token"] == "header-token-secret"
    assert JSON.unmarshal(captured["data"].decode("utf-8"), dict)["client_assertion"] == "assertion-secret"


@pytest.mark.asyncio
async def test_aexecute_redacts_sensitive_headers_and_body_from_debug_log(monkeypatch):
    captured = {}
    debug_logs = []
    body = {"client_assertion": "async-assertion-secret", "client_secret": "async-client-secret"}

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def request(self, method, url, *, headers=None, params=None, json=None, data=None, files=None,
                          timeout=None):
            captured["headers"] = dict(headers)
            captured["json"] = json
            return SimpleNamespace(status_code=200, headers={}, content=b"{}")

    monkeypatch.setattr(transport.httpx, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(transport.logger, "debug", lambda msg: debug_logs.append(msg))

    conf = Config()
    req = _request(body)
    req.token_types = {AccessTokenType.USER}
    option = RequestOption()
    option.user_access_token = "user-token-secret"

    await transport.Transport.aexecute(conf, req, option)

    log_output = "\n".join(debug_logs)
    assert "async-assertion-secret" not in log_output
    assert "async-client-secret" not in log_output
    assert "user-token-secret" not in log_output
    assert '"Authorization": "***"' in log_output
    assert '"client_secret": "***"' in log_output

    assert captured["headers"]["Authorization"] == "Bearer user-token-secret"
    assert captured["json"]["client_assertion"] == "async-assertion-secret"
