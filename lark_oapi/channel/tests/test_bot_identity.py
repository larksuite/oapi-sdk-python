"""Bot identity fetch — unit tests with mocked Transport."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from lark_oapi.channel.bot_identity import BotIdentity, fetch_bot_identity
from lark_oapi.core.model import Config, RawResponse


def _raw(body: dict, status: int = 200) -> RawResponse:
    r = RawResponse()
    r.status_code = status
    r.content = json.dumps(body).encode("utf-8")
    return r


def _fake_verify(cfg, request, option):
    """Stub `core.token.auth.verify` so unit tests don't hit the real
    tenant_access_token endpoint. The real function populates
    ``option.tenant_access_token``; we just write a sentinel here.
    """
    option.tenant_access_token = "t-test"


@pytest.mark.asyncio
async def test_fetch_uses_bot_v3_info_first():
    config = Config()
    config.app_id = "cli_x"
    config.app_secret = "sec"

    bot_v3_resp = _raw({
        "code": 0, "msg": "ok",
        "data": {"bot": {"open_id": "ou_bot_1", "user_id": "u1",
                         "app_name": "Demo Bot", "app_id": "cli_x"}},
    })
    with patch("lark_oapi.channel.bot_identity._verify_auth", side_effect=_fake_verify), \
            patch("lark_oapi.channel.bot_identity.Transport.aexecute",
                  new=AsyncMock(return_value=bot_v3_resp)):
        ident = await fetch_bot_identity(config)
    assert isinstance(ident, BotIdentity)
    assert ident.open_id == "ou_bot_1"
    assert ident.name == "Demo Bot"
    assert ident.user_id == "u1"


@pytest.mark.asyncio
async def test_fetch_falls_back_to_application_get():
    config = Config()
    config.app_id = "cli_y"
    config.app_secret = "sec"

    bot_v3_fail = _raw({"code": 99999, "msg": "blocked"})
    app_resp = _raw({
        "code": 0,
        "data": {"app": {"app_name": "App Y", "bot_info": {"open_id": "ou_fallback"}}},
    })
    calls = [bot_v3_fail, app_resp]

    async def fake_aexecute(cfg, req, opt):
        return calls.pop(0)

    with patch("lark_oapi.channel.bot_identity._verify_auth", side_effect=_fake_verify), \
            patch("lark_oapi.channel.bot_identity.Transport.aexecute", side_effect=fake_aexecute):
        ident = await fetch_bot_identity(config)
    assert ident is not None and ident.open_id == "ou_fallback"
    assert ident.name == "App Y"


@pytest.mark.asyncio
async def test_fetch_returns_none_on_all_failures():
    config = Config()
    config.app_id = "cli_z"
    config.app_secret = "sec"

    with patch("lark_oapi.channel.bot_identity._verify_auth", side_effect=_fake_verify), \
            patch("lark_oapi.channel.bot_identity.Transport.aexecute",
                  new=AsyncMock(side_effect=RuntimeError("network"))):
        ident = await fetch_bot_identity(config)
    assert ident is None


@pytest.mark.asyncio
async def test_fetch_handles_top_level_payload():
    """Regression: /bot/v3/info returns {bot, code, msg} with no `data`
    envelope — unlike most Feishu OpenAPI endpoints. The parser must
    unwrap both shapes or the fetch fails silently even on HTTP 200.
    """
    config = Config()
    config.app_id = "cli_t"
    config.app_secret = "sec"

    # Real shape observed from the production /bot/v3/info endpoint.
    flat_resp = _raw({
        "bot": {
            "open_id": "ou_real_bot",
            "app_name": "Demo Bot",
            "activate_status": 2,
        },
        "code": 0,
        "msg": "ok",
    })
    with patch("lark_oapi.channel.bot_identity._verify_auth", side_effect=_fake_verify), \
            patch("lark_oapi.channel.bot_identity.Transport.aexecute",
                  new=AsyncMock(return_value=flat_resp)):
        ident = await fetch_bot_identity(config)

    assert ident is not None, "flat payload must be parsed, not treated as failure"
    assert ident.open_id == "ou_real_bot"
    assert ident.name == "Demo Bot"


@pytest.mark.asyncio
async def test_fetch_injects_tenant_token_into_request():
    """Regression: `fetch_bot_identity` must run the auth-verify step before
    calling `Transport.aexecute`. Without it, `option.tenant_access_token`
    stays None and the outbound header becomes literal ``Bearer None``, which
    Feishu rejects with 400 — leaving bot identity unresolved and breaking
    group @Bot detection.
    """
    config = Config()
    config.app_id = "cli_w"
    config.app_secret = "sec"

    bot_v3_resp = _raw({
        "code": 0,
        "data": {"bot": {"open_id": "ou_bot", "app_id": "cli_w"}},
    })

    captured = {}

    async def spy_aexecute(cfg, req, opt):
        # Record the option.tenant_access_token that the caller prepared.
        captured["token"] = opt.tenant_access_token
        return bot_v3_resp

    # Stub `verify` so we don't actually hit the token endpoint but we *do*
    # observe that the verify step is invoked with the same (req, option)
    # that later reaches aexecute.
    with patch("lark_oapi.channel.bot_identity._verify_auth", side_effect=_fake_verify) as verify_mock, \
            patch("lark_oapi.channel.bot_identity.Transport.aexecute", side_effect=spy_aexecute):
        ident = await fetch_bot_identity(config)

    assert ident is not None and ident.open_id == "ou_bot"
    # Verify was actually called before aexecute (otherwise the captured
    # token would be None).
    assert verify_mock.called, "fetch_bot_identity must invoke token.auth.verify"
    assert captured["token"] == "t-test", (
        "tenant token must be set on option before aexecute — otherwise the "
        "request goes out with `Bearer None`"
    )
