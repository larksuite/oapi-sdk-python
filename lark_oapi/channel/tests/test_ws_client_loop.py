"""ws.Client event-loop isolation (issues #119 / #133).

Regression tests: each ws.Client must own a dedicated event loop (created
lazily, per instance) instead of sharing a module-level global loop, so
multi-bot setups work and a client constructed inside an already-running
loop is not bound to it.
"""

import asyncio

from lark_oapi.ws.client import Client


def make_client(app_id="cli_0000000000000001"):
    return Client(app_id=app_id, app_secret="secret")


def test_client_owns_a_dedicated_loop():
    c1 = make_client()
    c2 = make_client(app_id="cli_0000000000000002")
    l1 = c1._get_loop()
    l2 = c2._get_loop()
    assert l1 is not None
    # distinct instances never share a loop (the multi-bot race in #119)
    assert l1 is not l2
    # stable per instance
    assert c1._get_loop() is l1
    assert c2._get_loop() is l2
    l1.close()
    l2.close()


def test_no_module_level_loop_capture():
    import lark_oapi.ws.client as ws_mod

    assert not hasattr(ws_mod, "loop")


def test_loop_created_inside_running_loop_is_dedicated():
    async def inner():
        c = make_client()
        loop = c._get_loop()
        # never the caller's running loop (#133)
        assert loop is not asyncio.get_running_loop()
        loop.close()

    asyncio.run(inner())


def test_lock_created_lazily():
    c = make_client()
    assert c._lock is None
    lock = c._get_lock()
    assert isinstance(lock, asyncio.Lock)
    assert c._lock is lock
