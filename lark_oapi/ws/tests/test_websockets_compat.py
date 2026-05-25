from types import SimpleNamespace

import pytest

from lark_oapi.ws import client as ws_client
from lark_oapi.ws.const import (
    EXCEED_CONN_LIMIT,
    HEADER_HANDSHAKE_AUTH_ERRCODE,
    HEADER_HANDSHAKE_MSG,
    HEADER_HANDSHAKE_STATUS,
)
from lark_oapi.ws.exception import ClientException


class _FakeConn:
    async def close(self):
        pass


def test_parse_ws_connection_exception_reads_new_invalid_status_response_headers():
    exc = RuntimeError("handshake failed")
    exc.response = SimpleNamespace(
        headers={
            HEADER_HANDSHAKE_STATUS: "514",
            HEADER_HANDSHAKE_MSG: "too many connections",
            HEADER_HANDSHAKE_AUTH_ERRCODE: str(EXCEED_CONN_LIMIT),
        }
    )

    with pytest.raises(ClientException) as err:
        ws_client._parse_ws_conn_exception(exc)

    assert err.value.code == 514
    assert str(err.value) == "514: too many connections"


def test_parse_ws_connection_exception_keeps_legacy_headers_behavior():
    exc = RuntimeError("handshake failed")
    exc.headers = {
        HEADER_HANDSHAKE_STATUS: "514",
        HEADER_HANDSHAKE_MSG: "too many connections",
        HEADER_HANDSHAKE_AUTH_ERRCODE: str(EXCEED_CONN_LIMIT),
    }

    with pytest.raises(ClientException) as err:
        ws_client._parse_ws_conn_exception(exc)

    assert err.value.code == 514
    assert str(err.value) == "514: too many connections"


def test_get_conn_url_sends_custom_headers(monkeypatch):
    captured = {}

    def fake_post(url, *, headers=None, json=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return SimpleNamespace(
            status_code=200,
            content=b'{"code":0,"data":{"URL":"ws://example.test/callback?device_id=device&service_id=42"}}',
        )

    client = ws_client.Client(
        "app_id",
        "app_secret",
        headers={
            "x-tt-env": "boe",
            "x-use-ppe": "1",
            "locale": "en",
            ws_client.USER_AGENT: "custom-agent",
        },
    )
    monkeypatch.setattr(ws_client.requests, "post", fake_post)

    assert client._get_conn_url() == "ws://example.test/callback?device_id=device&service_id=42"
    assert captured["url"] == client._domain + ws_client.GEN_ENDPOINT_URI
    assert captured["json"] == {"AppID": "app_id", "AppSecret": "app_secret"}
    assert captured["headers"]["x-tt-env"] == "boe"
    assert captured["headers"]["x-use-ppe"] == "1"
    assert captured["headers"]["locale"] == "zh"
    assert captured["headers"][ws_client.USER_AGENT] == client._user_agent


@pytest.mark.asyncio
async def test_connect_disables_websockets_15_automatic_proxy(monkeypatch):
    captured = {}

    async def fake_connect(uri, *, proxy=True):
        captured["uri"] = uri
        captured["proxy"] = proxy
        return _FakeConn()

    client = ws_client.Client("app_id", "app_secret")
    monkeypatch.setattr(
        client,
        "_get_conn_url",
        lambda: "ws://example.test/callback?device_id=device&service_id=42",
    )
    monkeypatch.setattr(ws_client.websockets, "connect", fake_connect)
    monkeypatch.setattr(
        ws_client.loop,
        "create_task",
        lambda coro: coro.close() if hasattr(coro, "close") else None,
    )

    await client._connect()
    await client._disconnect()

    assert captured == {
        "uri": "ws://example.test/callback?device_id=device&service_id=42",
        "proxy": None,
    }


@pytest.mark.asyncio
async def test_connect_does_not_pass_proxy_to_older_websockets(monkeypatch):
    captured = {}

    async def fake_connect(uri):
        captured["uri"] = uri
        return _FakeConn()

    client = ws_client.Client("app_id", "app_secret")
    monkeypatch.setattr(
        client,
        "_get_conn_url",
        lambda: "ws://example.test/callback?device_id=device&service_id=42",
    )
    monkeypatch.setattr(ws_client.websockets, "connect", fake_connect)
    monkeypatch.setattr(
        ws_client.loop,
        "create_task",
        lambda coro: coro.close() if hasattr(coro, "close") else None,
    )

    await client._connect()
    await client._disconnect()

    assert captured == {
        "uri": "ws://example.test/callback?device_id=device&service_id=42",
    }
