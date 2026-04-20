"""Outbound regression probes for sender behaviour.

These tests pin the seams that test fakes patch (``send_driver``-returned
bound methods) so that future refactors do not silently break the patching
contract. The test suite intentionally only covers the seam the sender
actually calls; patches against ad-hoc instance attributes will not flow.

Only TC-103 represents an actual SDK-vs-harness behaviour gap: the harness
expects long ``{"markdown": ...}`` sends to be split into multiple chunks
with per-chunk message_ids surfaced on ``SendResult.chunk_ids``. The SDK
currently does neither. This test reproduces the failure.
"""

from typing import Any, Dict, List

import pytest

from lark_oapi.channel.config import OutboundConfig
from lark_oapi.channel.outbound.sender import OutboundSender, SendDriver
from lark_oapi.channel.types import OutboundPost, SendResult


def _driver():
    calls: List[Dict[str, Any]] = []

    async def create_message(**kwargs):
        calls.append({"op": "create", **kwargs})
        # Give each call a distinct message_id so a hypothetical chunked
        # send would yield a visible list of ids.
        return {
            "code": 0,
            "data": {"message_id": f"om_chunk_{len(calls)}"},
        }

    async def reply_message(**kwargs):
        calls.append({"op": "reply", **kwargs})
        return {"code": 0, "data": {"message_id": f"om_reply_{len(calls)}"}}

    return SendDriver(create_message=create_message, reply_message=reply_message), calls


# ---------------------------------------------------------------------------
# TC-103 — long-markdown chunking (FAILING — SDK gap)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tc103_long_markdown_send_result_exposes_chunk_ids():
    """Harness expects sending a very long markdown body to:

    1. Split into multiple chunks (multiple ``create_message`` driver calls).
    2. Expose the per-chunk message_ids via ``SendResult.chunk_ids``.

    SDK reality:
    - ``OutboundSender._materialize`` only chunks ``OutboundText``; for
      ``OutboundPost`` (which is what ``{"markdown": ...}`` coerces to) it
      returns a single-element body list regardless of length.
    - ``SendResult`` (see ``lark_oapi/channel/types.py``) has only
      ``success`` / ``message_id`` / ``error`` / ``raw`` — no
      ``chunk_ids`` field.

    This test is expected to FAIL against the current SDK. A fix would
    need to either (a) teach ``_materialize`` to markdown-split posts with
    the existing ``outbound.markdown.splitter`` and return multiple bodies,
    or (b) fall back to text-chunking for oversized markdown, and surface
    the per-chunk ids on ``SendResult``.
    """
    d, calls = _driver()
    s = OutboundSender(d, OutboundConfig(text_chunk_limit=1000))
    very_long = "paragraph\n" * 2000  # ~20 KB markdown

    result: SendResult = await s.send(
        OutboundPost(markdown=very_long), receive_id="oc_1"
    )

    assert result.success is True
    create_calls = [c for c in calls if c["op"] == "create"]
    # Harness assumption 1: long markdown is split.
    assert len(create_calls) >= 2, (
        f"expected long markdown to split into multiple chunks, got "
        f"{len(create_calls)} create_message call(s)"
    )
    # Harness assumption 2: SendResult exposes chunk_ids.
    chunk_ids = getattr(result, "chunk_ids", None)
    assert chunk_ids is not None, "SendResult has no chunk_ids attribute"
    assert isinstance(chunk_ids, list) and len(chunk_ids) >= 2
