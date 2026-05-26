import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from lark_oapi import Client
from lark_oapi.core import AccessTokenType, HttpMethod
from lark_oapi.core.cache import ICache
from lark_oapi.core.client_assertion import ClientAssertionToken
from lark_oapi.core.model import BaseRequest
from lark_oapi.ws import client as ws_client


class AbsoluteCache(ICache):
    def __init__(self):
        self.data = {}

    def get(self, key):
        item = self.data.get(key)
        return None if item is None else item[0]

    def set(self, key, value, expire):
        self.data[key] = (value, expire)


class RecordingProvider:
    def __init__(self):
        self.auds = []

    def retrieve_token(self, aud):
        self.auds.append(aud)
        return ClientAssertionToken("local-assertion")


class LocalState:
    def __init__(self):
        self.oauth_bodies = []
        self.ping_authorizations = []
        self.ws_bodies = []


def _serve(state):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length") or "0")
            body = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/oauth/v3/token":
                state.oauth_bodies.append(body)
                if body["grant_type"] == "authorization_code":
                    self._json({
                        "access_token": "user-token",
                        "token_type": "Bearer",
                        "expires_in": 7200,
                        "refresh_token": "refresh-token",
                    })
                    return
                if body["grant_type"] == "refresh_token":
                    self._json({"access_token": "refreshed-user-token", "expires_in": 7200})
                    return
                self._json({"access_token": "tenant-token", "expires_in": 7200})
                return
            if self.path == "/callback/ws/endpoint":
                state.ws_bodies.append(body)
                self._json({"code": 0, "data": {"URL": "ws://example.test/callback?device_id=device&service_id=42"}})
                return
            self.send_response(404)
            self.end_headers()

        def do_GET(self):
            if self.path == "/open-apis/mock/v1/ping":
                state.ping_authorizations.append(self.headers.get("Authorization"))
                self._json({"code": 0, "msg": "ok"})
                return
            self.send_response(404)
            self.end_headers()

        def _json(self, payload):
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def _ping_request():
    req = BaseRequest()
    req.http_method = HttpMethod.GET
    req.uri = "/open-apis/mock/v1/ping"
    req.token_types = {AccessTokenType.TENANT}
    return req


def test_local_keyless_openapi_access_token_and_ws_e2e():
    state = LocalState()
    server = _serve(state)
    base_url = f"http://127.0.0.1:{server.server_port}"
    provider = RecordingProvider()
    cache = AbsoluteCache()
    try:
        client = (
            Client.builder()
            .app_id("cli_local")
            .domain(base_url)
            .oauth_base_url(base_url)
            .client_assertion_provider(provider)
            .cache(cache)
            .build()
        )

        first = client.request(_ping_request())
        second = client.request(_ping_request())

        auth_code = client.access_token.retrieve_by_authorization_code(code="code")
        refreshed = client.access_token.refresh(refresh_token="refresh-token")

        ws = ws_client.Client("cli_local", "", domain=base_url, client_assertion_provider=provider)
        conn_url = ws._get_conn_url()

        assert first.code == 0
        assert second.code == 0
        assert state.ping_authorizations == ["Bearer tenant-token", "Bearer tenant-token"]
        assert auth_code.access_token == "user-token"
        assert refreshed.access_token == "refreshed-user-token"
        assert conn_url == "ws://example.test/callback?device_id=device&service_id=42"
        assert provider.auds == [
            f"127.0.0.1:{server.server_port}",
            f"127.0.0.1:{server.server_port}",
            f"127.0.0.1:{server.server_port}",
            f"127.0.0.1:{server.server_port}",
        ]
        assert len(state.oauth_bodies) == 3
        assert state.oauth_bodies[0]["grant_type"] == "urn:ietf:params:oauth:grant-type:jwt-bearer"
        assert state.oauth_bodies[0]["client_assertion"] == "local-assertion"
        assert state.ws_bodies == [{"AppID": "cli_local", "ClientAssertion": "local-assertion"}]
    finally:
        server.shutdown()
        server.server_close()
