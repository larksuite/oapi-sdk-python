import asyncio
import json
import os
import queue
import secrets
import threading
import time
import uuid
import webbrowser
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Iterable
from urllib.parse import parse_qs, urlsplit

import pytest
import websockets

from lark_oapi import Client
from lark_oapi.api.contact.v3.model.basic_batch_user_request import BasicBatchUserRequest
from lark_oapi.api.contact.v3.model.basic_batch_user_request_body import BasicBatchUserRequestBody
from lark_oapi.api.im.v1.model.create_message_request import CreateMessageRequest
from lark_oapi.api.im.v1.model.create_message_request_body import CreateMessageRequestBody
from lark_oapi.core.client_assertion import extract_aud_from_url
from lark_oapi.core.model import RequestOption
from lark_oapi.core.token import TokenManager
from lark_oapi.core.tests.e2e.client_assertion_live_harness import (
    MemoryCache,
    ModeEnvProvider,
    build_authorize_url,
    deploy_domains,
    install_host_resolver_override,
    load_e2e_env,
    parse_bool,
)
from lark_oapi.ws import client as ws_client


load_e2e_env()
install_host_resolver_override(os.environ.get("LARK_GDPR_PROXY_SERVICE"), os.environ.get("LARK_GDPR_PROXY_RESOLVE_IP"))

pytestmark = pytest.mark.skipif(
    os.environ.get("LARK_CLIENT_ASSERTION_E2E") != "1",
    reason="set LARK_CLIENT_ASSERTION_E2E=1 to run live ClientAssertion E2E",
)


def _require_env(names: Iterable[str]) -> Dict[str, str]:
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        pytest.skip("missing env: " + ", ".join(missing))
    return {name: os.environ[name] for name in names}


def _domains():
    return deploy_domains(os.environ.get("LARK_DEPLOY_ENV"))


def _build_app_secret_client():
    env = _require_env(["LARK_APP_ID", "LARK_APP_SECRET"])
    domains = _domains()
    return (
        Client.builder()
        .app_id(env["LARK_APP_ID"])
        .app_secret(env["LARK_APP_SECRET"])
        .domain(domains.openapi_domain)
        .oauth_base_url(domains.oauth_base_url)
        .cache(MemoryCache())
        .build()
    )


def _build_client_assertion_client(mode: str, provider: ModeEnvProvider = None):
    env = _require_env(["LARK_APP_ID"])
    if mode == "zti":
        _require_env(["LARK_ZTI_CLIENT_ASSERTION"])
    elif mode == "gdpr":
        _require_env([
            "LARK_GDPR_CLIENT_ASSERTION",
            "LARK_GDPR_PROXY_SERVICE",
            "LARK_GDPR_PROXY_PREFIX",
        ])
        if not os.environ["LARK_GDPR_PROXY_PREFIX"].startswith("/"):
            pytest.fail("LARK_GDPR_PROXY_PREFIX must start with /")
        if (os.environ.get("LARK_DEPLOY_ENV") or "online").lower() not in ("online", "prod", "production", "cn"):
            pytest.fail("GDPR proxy E2E must use LARK_DEPLOY_ENV=online")
    else:
        raise ValueError("mode must be zti or gdpr")

    provider = provider or ModeEnvProvider(mode)
    domains = _domains()
    client = (
        Client.builder()
        .app_id(env["LARK_APP_ID"])
        .client_assertion_provider(provider)
        .domain(domains.openapi_domain)
        .oauth_base_url(domains.oauth_base_url)
        .cache(MemoryCache())
        .build()
    )
    return client, provider


def _build_client_with_app_secret_and_provider(mode: str):
    env = _require_env(["LARK_APP_ID", "LARK_APP_SECRET"])
    provider = ModeEnvProvider(mode)
    domains = _domains()
    client = (
        Client.builder()
        .app_id(env["LARK_APP_ID"])
        .app_secret(env["LARK_APP_SECRET"])
        .client_assertion_provider(provider)
        .domain(domains.openapi_domain)
        .oauth_base_url(domains.oauth_base_url)
        .cache(MemoryCache())
        .build()
    )
    return client, provider


def _response_summary(resp) -> str:
    return "code={}, msg={}, log_id={}".format(resp.code, resp.msg, resp.get_log_id())


def _case_id(prefix: str) -> str:
    return "{}-{}".format(prefix, uuid.uuid4().hex[:8])


def _send_tat_message(client: Client, case_id: str) -> str:
    env = _require_env(["LARK_OPEN_ID"])
    body = (
        CreateMessageRequestBody.builder()
        .receive_id(env["LARK_OPEN_ID"])
        .msg_type("text")
        .content(json.dumps({"text": "ClientAssertion E2E TAT message: " + case_id}))
        .uuid(str(uuid.uuid4()))
        .build()
    )
    req = CreateMessageRequest.builder().receive_id_type("open_id").request_body(body).build()

    resp = client.im.v1.message.create(req)

    assert resp.success(), _response_summary(resp)
    assert resp.data is not None and resp.data.message_id
    return resp.data.message_id


def _call_basic_batch_with_uat(client: Client, user_access_token: str):
    env = _require_env(["LARK_OPEN_ID"])
    body = BasicBatchUserRequestBody.builder().user_ids([env["LARK_OPEN_ID"]]).build()
    req = BasicBatchUserRequest.builder().user_id_type("open_id").request_body(body).build()
    option = RequestOption.builder().user_access_token(user_access_token).build()

    resp = client.contact.v3.user.basic_batch(req, option)

    assert resp.success(), _response_summary(resp)
    assert resp.data is not None and resp.data.users
    assert resp.data.users[0].user_id


def _oauth_timeout_seconds() -> int:
    return int(os.environ.get("LARK_OAUTH_TIMEOUT_SECONDS") or "180")


@contextmanager
def _oauth_callback_server(redirect_uri: str, expected_state: str):
    parsed = urlsplit(redirect_uri)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("LARK_OAUTH_REDIRECT_URI must be a local http callback")
    if not parsed.port:
        raise ValueError("LARK_OAUTH_REDIRECT_URI must include a port")

    result_queue = queue.Queue(maxsize=1)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            callback = urlsplit(self.path)
            if callback.path != parsed.path:
                self.send_response(404)
                self.end_headers()
                return

            params = {key: values[0] for key, values in parse_qs(callback.query).items()}
            if params.get("state") != expected_state:
                self._send_text(400, "OAuth state mismatch.")
                result_queue.put({"error": "state_mismatch"})
                return

            if "code" not in params:
                self._send_text(400, "OAuth callback missing code.")
                params.setdefault("error", "missing_code")
                result_queue.put(params)
                return

            self._send_text(200, "OAuth callback received. You can close this tab.")
            result_queue.put(params)

        def _send_text(self, status: int, text: str):
            data = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer((parsed.hostname, parsed.port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield result_queue
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _authorize_and_exchange_code(client: Client):
    env = _require_env([
        "LARK_APP_ID",
        "LARK_OAUTH_REDIRECT_URI",
        "LARK_OAUTH_SCOPE",
    ])
    if parse_bool(os.environ.get("LARK_OAUTH_PKCE_REQUIRED"), default=False):
        pytest.fail("OAuth UAT E2E expects LARK_OAUTH_PKCE_REQUIRED=false")

    domains = _domains()
    state = secrets.token_urlsafe(24)
    auth_url = build_authorize_url(
        oauth_base_url=domains.oauth_base_url,
        app_id=env["LARK_APP_ID"],
        redirect_uri=env["LARK_OAUTH_REDIRECT_URI"],
        scope=env["LARK_OAUTH_SCOPE"],
        state=state,
    )

    with _oauth_callback_server(env["LARK_OAUTH_REDIRECT_URI"], state) as callback_queue:
        print("\nOpen this URL to authorize OAuth UAT E2E:\n{}".format(auth_url))
        webbrowser.open(auth_url)
        try:
            params = callback_queue.get(timeout=_oauth_timeout_seconds())
        except queue.Empty:
            pytest.fail("OAuth callback timed out")

    if params.get("error"):
        pytest.fail("OAuth callback failed: " + params["error"])
    return client.access_token.retrieve_by_authorization_code(
        code=params["code"],
        redirect_uri=env["LARK_OAUTH_REDIRECT_URI"],
        scope=env["LARK_OAUTH_SCOPE"],
    )


async def _connect_ws_once(conn_url: str, listen_seconds: int):
    kwargs = ws_client._ws_connect_kwargs()
    kwargs.setdefault("open_timeout", 10)
    kwargs.setdefault("close_timeout", 5)
    async with websockets.connect(conn_url, **kwargs):
        await asyncio.sleep(listen_seconds)


def _ws_listen_seconds() -> int:
    seconds = int(os.environ.get("LARK_WS_LISTEN_SECONDS") or "30")
    assert seconds > 0
    return seconds


def _assert_provider_received_aud(provider: ModeEnvProvider, expected_aud: str):
    assert expected_aud in provider.auds


@pytest.mark.slow
def test_live_provider_takes_precedence_over_app_secret():
    client, provider = _build_client_with_app_secret_and_provider("zti")

    token = TokenManager.get_self_tenant_token(client.config)

    assert token
    _assert_provider_received_aud(provider, extract_aud_from_url(_domains().oauth_base_url))


@pytest.mark.slow
def test_live_app_secret_tenant_token_and_tat_message():
    client = _build_app_secret_client()

    token = TokenManager.get_self_tenant_token(client.config)
    message_id = _send_tat_message(client, _case_id("SECRET-TAT"))

    assert token
    assert message_id


@pytest.mark.slow
@pytest.mark.parametrize("mode", ["zti", "gdpr"])
def test_live_client_assertion_tenant_token_and_tat_message(mode):
    client, provider = _build_client_assertion_client(mode)

    token = TokenManager.get_self_tenant_token(client.config)
    message_id = _send_tat_message(client, _case_id(mode.upper() + "-TAT"))

    assert token
    assert message_id
    _assert_provider_received_aud(provider, extract_aud_from_url(_domains().oauth_base_url))


@pytest.mark.slow
@pytest.mark.parametrize("mode", ["zti", "gdpr"])
def test_live_client_assertion_oauth_uat_authorization_code_refresh_and_basic_batch(mode):
    client, provider = _build_client_assertion_client(mode)

    token = _authorize_and_exchange_code(client)
    if not token.access_token:
        pytest.fail("authorization code exchange did not return access_token")
    _call_basic_batch_with_uat(client, token.access_token)

    if not token.refresh_token:
        pytest.fail("authorization code exchange did not return refresh_token; verify offline_access is enabled")
    refreshed = client.access_token.refresh(
        refresh_token=token.refresh_token,
        scope=os.environ.get("LARK_OAUTH_SCOPE"),
    )
    if not refreshed.access_token:
        pytest.fail("refresh token exchange did not return access_token")
    _call_basic_batch_with_uat(client, refreshed.access_token)
    _assert_provider_received_aud(provider, extract_aud_from_url(_domains().oauth_base_url))


@pytest.mark.slow
def test_live_app_secret_ws_real_connect():
    if not parse_bool(os.environ.get("LARK_WS_CONNECT_E2E"), default=False):
        pytest.skip("set LARK_WS_CONNECT_E2E=true to run real WS connect")
    env = _require_env(["LARK_APP_ID", "LARK_APP_SECRET"])
    domains = _domains()
    client = ws_client.Client(
        env["LARK_APP_ID"],
        env["LARK_APP_SECRET"],
        domain=domains.openapi_domain,
        auto_reconnect=False,
    )

    conn_url = client._get_conn_url()
    asyncio.run(_connect_ws_once(conn_url, _ws_listen_seconds()))


@pytest.mark.slow
@pytest.mark.parametrize("mode", ["zti", "gdpr"])
def test_live_client_assertion_ws_real_connect(mode):
    if not parse_bool(os.environ.get("LARK_WS_CONNECT_E2E"), default=False):
        pytest.skip("set LARK_WS_CONNECT_E2E=true to run real WS connect")
    env = _require_env(["LARK_APP_ID"])
    if mode == "zti":
        _require_env(["LARK_ZTI_CLIENT_ASSERTION"])
    else:
        _require_env(["LARK_GDPR_CLIENT_ASSERTION", "LARK_GDPR_PROXY_SERVICE", "LARK_GDPR_PROXY_PREFIX"])
    domains = _domains()
    provider = ModeEnvProvider(mode)
    client = ws_client.Client(
        env["LARK_APP_ID"],
        "",
        domain=domains.openapi_domain,
        auto_reconnect=False,
        client_assertion_provider=provider,
    )

    conn_url = client._get_conn_url()
    asyncio.run(_connect_ws_once(conn_url, _ws_listen_seconds()))
    _assert_provider_received_aud(provider, extract_aud_from_url(domains.openapi_domain))
