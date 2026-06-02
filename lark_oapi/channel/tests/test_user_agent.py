"""User-Agent construction + ``channel`` tag propagation.

Mirrors node-sdk ``utils/__tests__/user-agent.ts`` plus integration coverage
for FeishuChannel passing ``extra_ua_tags=["channel"]`` into the underlying
HTTP and WebSocket clients.
"""

import re

from lark_oapi.channel import FeishuChannel
from lark_oapi.client import Client
from lark_oapi.core.const import PROJECT, USER_AGENT, VERSION
from lark_oapi.core.http.transport import _build_header
from lark_oapi.core.model.base_request import BaseRequest
from lark_oapi.core.model.config import Config
from lark_oapi.core.model.request_option import RequestOption
from lark_oapi.core.utils.user_agent import build_user_agent
from lark_oapi.ws.client import Client as WSClient

_BASE = f"{PROJECT}/v{VERSION}"


# ---------------------------------------------------------------------------
# build_user_agent — port of node-sdk tests
# ---------------------------------------------------------------------------


def test_base_ua_when_no_source_or_tags():
    assert build_user_agent() == _BASE


def test_source_appended_as_product_token():
    assert build_user_agent("cursor-bot") == f"{_BASE} source/cursor-bot"


def test_source_with_invalid_chars_is_sanitized():
    # all-invalid source still produces an empty token → drop the segment
    assert build_user_agent("机器人") == f"{_BASE} source/___"


def test_extra_tags_appended_as_bare_tokens_after_source():
    ua = build_user_agent("cursor-bot", extra_tags=["channel"])
    assert re.match(rf"^{re.escape(_BASE)} source/cursor-bot channel$", ua)


def test_extra_tags_appended_even_without_source():
    ua = build_user_agent(extra_tags=["channel"])
    assert ua == f"{_BASE} channel"


def test_multiple_extra_tags_appended_in_order():
    ua = build_user_agent("x", extra_tags=["channel", "beta"])
    assert "source/x channel beta" in ua


def test_extra_tags_are_sanitized():
    ua = build_user_agent(extra_tags=["has space"])
    assert "has_space" in ua


def test_empty_extra_tag_is_dropped():
    ua = build_user_agent("x", extra_tags=[""])
    assert ua == f"{_BASE} source/x"


# ---------------------------------------------------------------------------
# transport._build_header — UA wired through Config
# ---------------------------------------------------------------------------


def _new_request() -> BaseRequest:
    req = BaseRequest()
    req.headers = {}
    req.token_types = set()
    return req


def test_transport_ua_contains_source_and_extra_tags():
    cfg = Config()
    cfg.source = "cursor-bot"
    cfg.extra_ua_tags = ["channel"]
    headers = _build_header(_new_request(), RequestOption(), cfg)
    assert headers[USER_AGENT] == f"{_BASE} source/cursor-bot channel"


def test_transport_ua_falls_back_to_base_when_conf_none():
    headers = _build_header(_new_request(), RequestOption(), None)
    assert headers[USER_AGENT] == _BASE


# ---------------------------------------------------------------------------
# FeishuChannel propagates ``channel`` tag into both clients
# ---------------------------------------------------------------------------


def test_channel_sets_extra_ua_tags_on_underlying_client():
    ch = FeishuChannel(app_id="cli_test", app_secret="secret")
    try:
        assert ch.client._config is not None
        assert ch.client._config.extra_ua_tags == ["channel"]
    finally:
        # Channel construction starts no background loops; nothing to tear
        # down beyond letting the object go out of scope.
        pass


def test_ws_client_ua_includes_channel_tag():
    ws = WSClient(
        app_id="cli_test",
        app_secret="secret",
        extra_ua_tags=["channel"],
    )
    assert ws._user_agent == f"{_BASE} channel"


def test_ws_client_default_ua_has_no_extra_tag():
    ws = WSClient(app_id="cli_test", app_secret="secret")
    assert ws._user_agent == _BASE


# ---------------------------------------------------------------------------
# ClientBuilder.source() exposes the public knob
# ---------------------------------------------------------------------------


def test_client_builder_source_propagates_to_config():
    client = (
        Client.builder()
        .app_id("cli_test")
        .app_secret("secret")
        .source("my-bot")
        .build()
    )
    assert client._config.source == "my-bot"
