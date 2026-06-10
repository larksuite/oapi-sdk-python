from pathlib import Path

import pytest

from lark_oapi.core.client_assertion import TargetInfo
from lark_oapi.core.tests.e2e.client_assertion_live_harness import (
    BOE_DOMAINS,
    ONLINE_DOMAINS,
    ModeEnvProvider,
    build_host_override_getaddrinfo,
    build_authorize_url,
    decode_jwt_payload_unverified,
    deploy_domains,
    load_env_file,
    parse_bool,
)


def test_parse_bool_accepts_common_values():
    assert parse_bool("true") is True
    assert parse_bool("1") is True
    assert parse_bool("yes") is True
    assert parse_bool("false") is False
    assert parse_bool("0") is False
    assert parse_bool(None, default=True) is True


def test_deploy_domains_supports_online_and_boe():
    assert deploy_domains("online") == ONLINE_DOMAINS
    assert deploy_domains("cn") == ONLINE_DOMAINS
    assert deploy_domains("boe") == BOE_DOMAINS

    with pytest.raises(ValueError, match="LARK_DEPLOY_ENV"):
        deploy_domains("lark")


def test_load_env_file_preserves_existing_env_and_handles_quotes(tmp_path: Path):
    env_file = tmp_path / ".env.e2e"
    env_file.write_text(
        "\n".join(
            [
                "# comment",
                "export LARK_APP_ID=cli_file",
                'LARK_OAUTH_SCOPE="contact:user.basic_profile:readonly offline_access"',
                "LARK_APP_SECRET=from_file # inline comment",
            ]
        ),
        encoding="utf-8",
    )
    env = {"LARK_APP_ID": "cli_existing"}

    load_env_file(env_file, env=env)

    assert env["LARK_APP_ID"] == "cli_existing"
    assert env["LARK_OAUTH_SCOPE"] == "contact:user.basic_profile:readonly offline_access"
    assert env["LARK_APP_SECRET"] == "from_file"


def test_mode_env_provider_returns_zti_without_target_info():
    env = {"LARK_ZTI_CLIENT_ASSERTION": "zti-token"}
    provider = ModeEnvProvider("zti", env=env)

    token = provider.retrieve_token("accounts.feishu.cn")

    assert token.value == "zti-token"
    assert token.target_info is None
    assert provider.auds == ["accounts.feishu.cn"]


def test_mode_env_provider_returns_gdpr_with_target_info():
    env = {
        "LARK_GDPR_CLIENT_ASSERTION": "gdpr-token",
        "LARK_GDPR_PROXY_SERVICE": "gdpr-proxy.example.internal",
        "LARK_GDPR_PROXY_PREFIX": "/proxy/example",
    }
    provider = ModeEnvProvider("gdpr", env=env)

    token = provider.retrieve_token("open.feishu.cn")

    assert token.value == "gdpr-token"
    assert token.target_info == TargetInfo("gdpr-proxy.example.internal", "/proxy/example")
    assert provider.auds == ["open.feishu.cn"]


def test_build_authorize_url_uses_local_redirect_without_pkce():
    url = build_authorize_url(
        oauth_base_url="https://accounts.feishu.cn",
        app_id="cli_xxx",
        redirect_uri="http://127.0.0.1:8765/uat_e2e/callback",
        scope="contact:user.basic_profile:readonly offline_access",
        state="state-123",
    )

    assert url.startswith("https://accounts.feishu.cn/open-apis/authen/v1/authorize?")
    assert "app_id=cli_xxx" in url
    assert "redirect_uri=http%3A%2F%2F127.0.0.1%3A8765%2Fuat_e2e%2Fcallback" in url
    assert "scope=contact%3Auser.basic_profile%3Areadonly+offline_access" in url
    assert "state=state-123" in url
    assert "code_challenge" not in url


def test_decode_jwt_payload_unverified_decodes_payload():
    token = "header.eyJleHAiOjEyMywiYXVkIjpbImFjY291bnRzLmZlaXNodS5jbiJdfQ.signature"

    payload = decode_jwt_payload_unverified(token)

    assert payload == {"exp": 123, "aud": ["accounts.feishu.cn"]}


def test_build_host_override_getaddrinfo_only_rewrites_target_host():
    calls = []

    def fake_getaddrinfo(host, port, family, type_arg, proto_arg, flags_arg):
        calls.append((host, port, family, type_arg, proto_arg, flags_arg))
        return [("result", host, family)]

    resolver = build_host_override_getaddrinfo(
        fake_getaddrinfo,
        "gdpr-proxy.example.internal",
        "192.0.2.10",
    )

    assert resolver("gdpr-proxy.example.internal", 443, 0, 1, 2, 3) == [("result", "192.0.2.10", 2)]
    assert resolver("open.feishu.cn", 443, 0, 1, 2, 3) == [("result", "open.feishu.cn", 0)]
