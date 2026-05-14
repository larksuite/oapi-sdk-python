"""DeviceFlowClient tests with a mocked httpx transport."""

from typing import Any, Dict, List

import httpx
import pytest

from lark_oapi.channel.auth.device_flow import DeviceFlowClient, uat_needs_refresh
from lark_oapi.channel.errors import UATAuthError
from lark_oapi.channel.types import UAT


def _mock_transport(responses: List[Dict[str, Any]]):
    """Build an httpx MockTransport that returns the next response on each call."""
    idx = [0]

    def handler(request: httpx.Request) -> httpx.Response:
        if idx[0] >= len(responses):
            return httpx.Response(500, json={"msg": "no more canned responses"})
        r = responses[idx[0]]
        idx[0] += 1
        return httpx.Response(200, json=r)

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_start_returns_device_init():
    transport = _mock_transport(
        [
            {
                "verification_uri": "https://x/auth",
                "verification_uri_complete": "https://x/auth?user_code=ABCD",
                "user_code": "ABCD",
                "device_code": "dc_1",
                "expires_in": 600,
                "interval": 5,
            }
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    df = DeviceFlowClient("cli", "sec", http_client=client)
    init = await df.start(["im:message"])
    assert init.device_code == "dc_1"
    assert init.user_code == "ABCD"
    assert init.interval == 5
    assert "user_code=ABCD" in init.verification_uri_complete


@pytest.mark.asyncio
async def test_poll_returns_uat_on_success():
    transport = _mock_transport(
        [
            {
                "access_token": "tok_x",
                "refresh_token": "rtok",
                "expires_in": 7200,
                "refresh_token_expires_in": 2592000,
                "scope": "im:message",
            }
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    df = DeviceFlowClient("cli", "sec", http_client=client)
    uat = await df.poll("dc_1", interval=1, timeout_seconds=10)
    assert uat.access_token == "tok_x"
    assert uat.refresh_token == "rtok"
    assert "im:message" in uat.scopes


@pytest.mark.asyncio
async def test_poll_access_denied_raises():
    transport = _mock_transport([{"error": "access_denied", "msg": "user denied"}])
    client = httpx.AsyncClient(transport=transport)
    df = DeviceFlowClient("cli", "sec", http_client=client)
    with pytest.raises(UATAuthError):
        await df.poll("dc_1", interval=1, timeout_seconds=3)


@pytest.mark.asyncio
async def test_poll_pending_then_ok():
    # First response: authorization_pending; second: success.
    transport = _mock_transport(
        [
            {"error": "authorization_pending"},
            {"access_token": "t", "expires_in": 300, "scope": "im:message"},
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    df = DeviceFlowClient("cli", "sec", http_client=client)
    uat = await df.poll("dc_1", interval=0, timeout_seconds=10)
    assert uat.access_token == "t"


def test_uat_needs_refresh_threshold():
    import time

    soon = UAT(access_token="t", expires_at=time.time() + 60)
    later = UAT(access_token="t", expires_at=time.time() + 1800)
    assert uat_needs_refresh(soon, slack_seconds=300) is True
    assert uat_needs_refresh(later, slack_seconds=300) is False


@pytest.mark.asyncio
async def test_refresh_uses_refresh_token():
    transport = _mock_transport(
        [{"access_token": "fresh", "refresh_token": "r2", "expires_in": 600, "scope": "im:message"}]
    )
    client = httpx.AsyncClient(transport=transport)
    df = DeviceFlowClient("cli", "sec", http_client=client)
    uat = await df.refresh("r1")
    assert uat.access_token == "fresh"
    assert uat.refresh_token == "r2"
