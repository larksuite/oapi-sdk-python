import os

import pytest

from lark_oapi import Client
from lark_oapi.core.client_assertion import ClientAssertionToken
from lark_oapi.core.token import TokenManager
from lark_oapi.ws import client as ws_client


class EnvProvider:
    def retrieve_token(self, aud):
        return ClientAssertionToken(os.environ["LARK_CLIENT_ASSERTION"])


pytestmark = pytest.mark.skipif(
    os.environ.get("LARK_CLIENT_ASSERTION_E2E") != "1",
    reason="set LARK_CLIENT_ASSERTION_E2E=1 to run live keyless E2E",
)


def _client():
    app_id = os.environ.get("LARK_APP_ID")
    assertion = os.environ.get("LARK_CLIENT_ASSERTION")
    if not app_id or not assertion:
        pytest.skip("LARK_APP_ID and LARK_CLIENT_ASSERTION are required")

    builder = Client.builder().app_id(app_id).client_assertion_provider(EnvProvider())
    if os.environ.get("LARK_OPENAPI_DOMAIN"):
        builder.domain(os.environ["LARK_OPENAPI_DOMAIN"])
    if os.environ.get("LARK_OAUTH_BASE_URL"):
        builder.oauth_base_url(os.environ["LARK_OAUTH_BASE_URL"])
    return builder.build()


def test_live_tenant_token_exchange_smoke():
    client = _client()

    token = TokenManager.get_self_tenant_token(client.config)

    assert token


def test_live_authorization_code_exchange_smoke():
    code = os.environ.get("LARK_OAUTH_CODE")
    if not code:
        pytest.skip("LARK_OAUTH_CODE is required")

    resp = _client().access_token.retrieve_by_authorization_code(code=code)

    assert resp.access_token


def test_live_refresh_token_smoke():
    refresh_token = os.environ.get("LARK_REFRESH_TOKEN")
    if not refresh_token:
        pytest.skip("LARK_REFRESH_TOKEN is required")

    resp = _client().access_token.refresh(refresh_token=refresh_token)

    assert resp.access_token


def test_live_ws_bootstrap_smoke():
    if os.environ.get("LARK_WS_CLIENT_ASSERTION_E2E") != "1":
        pytest.skip("set LARK_WS_CLIENT_ASSERTION_E2E=1 to run WS live smoke")
    app_id = os.environ.get("LARK_APP_ID")
    if not app_id or not os.environ.get("LARK_CLIENT_ASSERTION"):
        pytest.skip("LARK_APP_ID and LARK_CLIENT_ASSERTION are required")

    client = ws_client.Client(
        app_id,
        "",
        domain=os.environ.get("LARK_OPENAPI_DOMAIN", "https://open.feishu.cn"),
        client_assertion_provider=EnvProvider(),
    )

    conn_url = client._get_conn_url()

    assert conn_url.startswith(("ws://", "wss://"))
