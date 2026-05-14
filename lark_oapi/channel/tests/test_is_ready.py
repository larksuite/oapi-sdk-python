"""is_ready / wait_ready behavior.

These tests poke FeishuChannel at the API surface, not the WS layer. They
flip the readiness event manually to confirm the property and the await
behavior, since spinning a real WS connection in unit tests is unreasonable.
"""

import asyncio
import pytest

from lark_oapi.channel import FeishuChannel


def test_is_ready_false_before_start():
    ch = FeishuChannel(app_id="cli_x", app_secret="x")
    assert ch.is_ready is False


@pytest.mark.asyncio
async def test_wait_ready_resolves_when_event_set():
    ch = FeishuChannel(app_id="cli_x", app_secret="x")
    loop = asyncio.get_running_loop()

    async def flip_after():
        await asyncio.sleep(0.05)
        ch._mark_ready()  # internal API, used in tests

    loop.create_task(flip_after())
    await asyncio.wait_for(ch.wait_ready(), timeout=1.0)
    assert ch.is_ready is True


@pytest.mark.asyncio
async def test_wait_ready_timeout_raises():
    ch = FeishuChannel(app_id="cli_x", app_secret="x")
    with pytest.raises(asyncio.TimeoutError):
        await ch.wait_ready(timeout=0.05)
