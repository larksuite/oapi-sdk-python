import inspect

import websockets

from lark_oapi.ws.client import Client, _ws_connect_kwargs


def make_client(**kwargs):
    return Client("app_id", "app_secret", **kwargs)


def test_default_preserves_historical_direct_connect():
    c = make_client()
    assert c._resolved_ws_connect_kwargs() == _ws_connect_kwargs()


def test_explicit_proxy_kwarg_wins_over_forced_direct_connect():
    c = make_client(ws_connect_kwargs={"proxy": "http://proxy.example:8080"})
    resolved = c._resolved_ws_connect_kwargs()
    assert resolved["proxy"] == "http://proxy.example:8080"


def test_env_discovery_enabled_when_caller_opt_in_without_proxy():
    # On websockets >= 15 the SDK forces proxy=None by default; an explicit
    # (even empty) ws_connect_kwargs drops that flag so HTTP_PROXY etc. work.
    c = make_client(ws_connect_kwargs={})
    resolved = c._resolved_ws_connect_kwargs()
    assert "proxy" not in resolved
    # Other legacy kwargs (if any on this websockets version) are preserved.
    base = _ws_connect_kwargs()
    base.pop("proxy", None)
    assert resolved == base


def test_caller_values_merge_with_sdk_defaults():
    c = make_client(ws_connect_kwargs={"max_size": 2 ** 21})
    resolved = c._resolved_ws_connect_kwargs()
    assert resolved["max_size"] == 2 ** 21
    if "proxy" in inspect.signature(websockets.connect).parameters:
        # proxy: None was dropped, not merged.
        assert "proxy" not in resolved


def test_connect_signature_detection_still_works():
    params = inspect.signature(websockets.connect).parameters
    base = _ws_connect_kwargs()
    if "proxy" in params:
        assert base == {"proxy": None}
    else:
        assert base == {}
