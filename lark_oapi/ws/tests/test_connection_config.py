from types import SimpleNamespace

import pytest

from lark_oapi.ws import client as ws_client
from lark_oapi.ws.connection_config import build_connection_url
from lark_oapi.ws.exception import ClientException


@pytest.mark.parametrize("host", ["example.test", "example.test:443", "127.0.0.1:80", "[::1]", "[::1]:443"])
def test_host_override_retains_raw_path_and_query(host):
    ws_client.Client("app", "placeholder", connection_host=host)
    endpoint = "wss://original.test/a%2Fb?device_id=d&x=%2F&x=2"
    assert build_connection_url(endpoint, host) == "wss://" + host + "/a%2Fb?device_id=d&x=%2F&x=2"
    assert build_connection_url(endpoint, None) == endpoint


@pytest.mark.parametrize("host", ["", " ", "https://x", "x/path", "x?q=1", 123])
def test_invalid_host_is_rejected_before_network(host):
    with pytest.raises(ValueError, match="invalid websocket connection host"):
        ws_client.Client("app", "placeholder", connection_host=host)


@pytest.mark.parametrize("headers", [
    {name: "value"} for name in ["Host", "cOnNeCtIoN", "Upgrade", "sEc-WeBsOcKeT-Key"]
])
def test_invalid_headers_are_rejected_before_network(headers):
    with pytest.raises(ValueError, match="invalid websocket connection headers"):
        ws_client.Client("app", "placeholder", connection_headers=headers)


@pytest.mark.parametrize("endpoint", ["https://x/ws", "wss://user@x/ws", "wss://x/ws#", "wss:///path"])
def test_invalid_overridden_endpoint_is_terminal(endpoint):
    with pytest.raises(ClientException) as err:
        build_connection_url(endpoint, "logical.test")
    assert err.value.code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("new_api", [False, True])
async def test_handshake_isolation_snapshot_and_reconnect(monkeypatch, new_api):
    requests = []
    handshakes = []

    def fake_post(url, *, headers, json):
        requests.append((url, headers))
        return SimpleNamespace(status_code=200, content=b'{"code":0,"data":{"URL":"wss://original.test/a%2Fb?device_id=d&service_id=42&x=%2F&x=2"}}')

    class FakeConnection:
        async def close(self):
            pass

    def capture(uri, headers, proxy):
        handshakes.append((uri, dict(headers), proxy))
        # A transport may mutate its own copy; the next attempt must be unaffected.
        headers["X-Route"] = "transport-mutated"
        return FakeConnection()

    async def legacy_connect(uri, *, extra_headers, compression="deflate"):
        return capture(uri, extra_headers, "not-passed")

    async def modern_connect(uri, *, additional_headers, proxy=True, compression="deflate"):
        return capture(uri, additional_headers, proxy)

    configured = {"X-Route": "ws-only"}
    client = ws_client.Client("app", "placeholder", domain="https://bootstrap.test",
                              headers={"X-Bootstrap": "http-only"},
                              connection_host="logical.test:8443", connection_headers=configured)
    configured["X-Route"] = "caller-mutated"
    monkeypatch.setattr(ws_client.requests, "post", fake_post)
    monkeypatch.setattr(ws_client.websockets, "connect", modern_connect if new_api else legacy_connect)
    monkeypatch.setattr(ws_client.loop, "create_task", lambda coro: coro.close())
    for _ in range(2):
        await client._connect()
        await client._disconnect()
    assert len(requests) == len(handshakes) == 2
    for url, headers in requests:
        assert url == "https://bootstrap.test" + ws_client.GEN_ENDPOINT_URI
        assert headers["X-Bootstrap"] == "http-only"
        assert "X-Route" not in headers
    for uri, headers, proxy in handshakes:
        assert uri == "wss://logical.test:8443/a%2Fb?device_id=d&service_id=42&x=%2F&x=2"
        assert headers == {"X-Route": "ws-only"}
        assert proxy == (None if new_api else "not-passed")
