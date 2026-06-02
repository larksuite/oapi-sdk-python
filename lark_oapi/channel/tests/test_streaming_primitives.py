"""Unit tests for UpdateQueue / merge_streaming_text / Throttle /
MarkdownStreamController / CardStreamController."""

import asyncio
from typing import Any, Dict, List

import pytest

from lark_oapi.channel.outbound.streaming import (
    Throttle,
    UpdateQueue,
    merge_streaming_text,
)
from lark_oapi.channel.outbound.streaming.card_stream import CardStreamController
from lark_oapi.channel.outbound.streaming.markdown_stream import MarkdownStreamController


# ---- merge_streaming_text ---------------------------------------------------


def test_merge_accumulated_uses_next():
    assert merge_streaming_text("Hello", "Hello world") == "Hello world"


def test_merge_delta_concatenates():
    assert merge_streaming_text("Hello", " world") == "Hello world"


def test_merge_rewound_keeps_prev():
    assert merge_streaming_text("Hello world", "Hello") == "Hello world"


def test_merge_overlap_detected():
    assert merge_streaming_text("Hello wo", "world!") == "Hello world!"


def test_merge_no_overlap_falls_back_to_concat():
    assert merge_streaming_text("abc", "xyz") == "abcxyz"


def test_merge_empty_inputs():
    assert merge_streaming_text("", "hi") == "hi"
    assert merge_streaming_text("hi", "") == "hi"


# ---- UpdateQueue ------------------------------------------------------------
#
# UpdateQueue is coalescing: at most 1 running + 1 pending. A burst of
# enqueues while a task is running collapses down to a single "latest"
# pending. See update_queue.py docstring for the semantic contract and
# the intentional divergence from node-sdk's strict FIFO.


@pytest.mark.asyncio
async def test_update_queue_runs_sequentially_when_not_bursted():
    """When enqueues are spaced out (each runs to completion before the
    next is enqueued), the queue behaves like a simple FIFO."""
    q = UpdateQueue()
    log: List[str] = []

    async def mk(name, sleep):
        async def t():
            log.append(f"{name}:start")
            await asyncio.sleep(sleep)
            log.append(f"{name}:end")

        return t

    for name, sleep in (("A", 0.01), ("B", 0.01), ("C", 0.01)):
        q.enqueue(await mk(name, sleep))
        await q.drain()
    assert log == ["A:start", "A:end", "B:start", "B:end", "C:start", "C:end"]


@pytest.mark.asyncio
async def test_update_queue_coalesces_pending_bursts():
    """Burst-enqueue while a task is running: only the LAST enqueued task
    actually runs after the current one finishes. Intermediates are dropped.
    """
    q = UpdateQueue()
    ran: List[str] = []

    async def t_slow():
        ran.append("A:start")
        await asyncio.sleep(0.05)  # long enough to enqueue B, C, D during A
        ran.append("A:end")

    def mk(name):
        async def t():
            ran.append(name)

        return t

    q.enqueue(t_slow)
    # Let A actually start.
    await asyncio.sleep(0)
    # Burst B, C, D while A is mid-flight — only D should survive.
    q.enqueue(mk("B"))
    q.enqueue(mk("C"))
    q.enqueue(mk("D"))
    await q.drain()

    assert ran == ["A:start", "A:end", "D"], (
        f"expected A then only D (coalesced), got {ran}"
    )


@pytest.mark.asyncio
async def test_update_queue_continues_after_failure():
    """A raising task is logged + skipped; a subsequent enqueue still runs."""
    q = UpdateQueue()
    ran: List[str] = []

    async def fail():
        ran.append("fail:start")
        raise RuntimeError("boom")

    async def success():
        ran.append("success:ran")

    q.enqueue(fail)
    await asyncio.sleep(0)  # let fail() start
    q.enqueue(success)
    await q.drain()
    assert ran == ["fail:start", "success:ran"]


@pytest.mark.asyncio
async def test_update_queue_drain_with_no_enqueued_tasks_returns_immediately():
    q = UpdateQueue()
    # No enqueue — drain should be a no-op.
    await q.drain()


@pytest.mark.asyncio
async def test_update_queue_enqueue_after_drain_still_works():
    """After a drain, a fresh enqueue should still run (queue not 'closed')."""
    q = UpdateQueue()
    ran: List[str] = []

    async def t(name):
        ran.append(name)

    q.enqueue(lambda: t("first"))
    await q.drain()
    q.enqueue(lambda: t("second"))
    await q.drain()
    assert ran == ["first", "second"]


# ---- Throttle ---------------------------------------------------------------


@pytest.mark.asyncio
async def test_throttle_fires_on_chars_threshold():
    fires = []
    t = Throttle(min_ms=1000, min_chars=10, on_fire=lambda: fires.append(1))
    t.note(5)
    assert fires == []  # below char threshold, timer armed
    t.note(10)  # pending=15 ≥ 10 → immediate fire
    assert len(fires) == 1


@pytest.mark.asyncio
async def test_throttle_fires_on_time_threshold():
    fires = []
    t = Throttle(min_ms=50, min_chars=1000, on_fire=lambda: fires.append(1))
    t.note(5)
    await asyncio.sleep(0.1)
    assert len(fires) == 1


@pytest.mark.asyncio
async def test_throttle_flush_now_forces_fire():
    fires = []
    t = Throttle(min_ms=1000, min_chars=1000, on_fire=lambda: fires.append(1))
    t.note(5)
    t.flush_now()
    assert len(fires) == 1


@pytest.mark.asyncio
async def test_throttle_dispose_prevents_fire():
    fires = []
    t = Throttle(min_ms=30, min_chars=1000, on_fire=lambda: fires.append(1))
    t.note(5)
    t.dispose()
    await asyncio.sleep(0.08)
    assert fires == []


# ---- MarkdownStreamController (cardkit preallocation flow) -----------------


def _make_cardkit_fakes():
    """Return 4 fake cardkit dependencies + capture storage.

    Mirrors node's protocol: create_card_instance → send_card_by_reference →
    update_card_element_content (many times, seq-ordered) → finish_streaming_card.
    """
    state = {
        "created_specs": [],
        "sent_refs": [],
        "elem_updates": [],  # list of (card_id, element_id, content, seq)
        "finishes": [],  # list of (card_id, seq)
    }

    async def create_card_instance(spec):
        state["created_specs"].append(spec)
        return "card_abc"

    class _FakeSendResult:
        def __init__(self, mid): self.message_id = mid

    async def send_card_by_reference(to, card_id, *, receive_id_type=None,
                                     reply_to=None, reply_in_thread=None):
        state["sent_refs"].append({
            "to": to, "card_id": card_id,
            "receive_id_type": receive_id_type,
            "reply_to": reply_to, "reply_in_thread": reply_in_thread,
        })
        return _FakeSendResult("om_sent")

    async def update_card_element_content(card_id, element_id, content, seq):
        state["elem_updates"].append((card_id, element_id, content, seq))

    async def finish_streaming_card(card_id, seq):
        state["finishes"].append((card_id, seq))

    return state, (
        create_card_instance, send_card_by_reference,
        update_card_element_content, finish_streaming_card,
    )


def _mk_controller(deps, *, to="oc_1", rit="chat_id"):
    cci, scbr, ucec, fsc = deps
    return MarkdownStreamController(
        to=to, receive_id_type=rit, reply_to=None, reply_in_thread=None,
        create_card_instance=cci,
        send_card_by_reference=scbr,
        update_card_element_content=ucec,
        finish_streaming_card=fsc,
        min_ms=10, min_chars=3,
    )


@pytest.mark.asyncio
async def test_markdown_stream_creates_then_element_updates():
    state, deps = _make_cardkit_fakes()
    ctl = _mk_controller(deps)

    async def producer(s):
        await s.append("Hello ")
        await s.append("world")
        await s.append("!")

    mid = await ctl.run(producer)
    assert mid == "om_sent"

    # Creation happened exactly once, with a card spec containing a markdown
    # element whose element_id matches what updates target.
    assert len(state["created_specs"]) == 1
    spec = state["created_specs"][0]
    elements = spec["body"]["elements"]
    assert len(elements) == 1
    assert elements[0]["tag"] == "markdown"
    assert elements[0]["element_id"] == "stream_md"
    assert spec["config"]["streaming_mode"] is True

    # The reference send used the created card_id and the correct routing.
    assert len(state["sent_refs"]) == 1
    assert state["sent_refs"][0]["card_id"] == "card_abc"
    assert state["sent_refs"][0]["receive_id_type"] == "chat_id"

    # At least one element update fired; all target the same (card_id, element_id).
    assert len(state["elem_updates"]) >= 1
    assert all(cid == "card_abc" and eid == "stream_md"
               for (cid, eid, _c, _s) in state["elem_updates"])

    # Sequence numbers strictly increase — gaps are allowed because the
    # UpdateQueue is coalescing: when a snapshot is enqueued while another
    # is already pending, the pending one is replaced and its seq is
    # effectively skipped. The server orders by seq regardless.
    seqs = [s for (_c, _e, _txt, s) in state["elem_updates"]]
    assert seqs[0] >= 1, f"first seq should be >= 1, got {seqs}"
    assert all(later > earlier for earlier, later in zip(seqs, seqs[1:])), (
        f"seqs must be strictly increasing, got {seqs}"
    )

    # Last element-update content contains the full accumulated text.
    assert "Hello world!" in state["elem_updates"][-1][2]

    # finish_streaming_card called exactly once, with a seq greater than
    # any element-update seq (and greater than the controller's internal
    # counter which increments for every enqueue, coalesced or not).
    assert len(state["finishes"]) == 1
    finish_card_id, finish_seq = state["finishes"][0]
    assert finish_card_id == "card_abc"
    assert finish_seq > seqs[-1], (
        f"finish seq ({finish_seq}) must be after last update seq ({seqs[-1]})"
    )


@pytest.mark.asyncio
async def test_markdown_stream_sequence_never_rewinds():
    """Seq is strictly monotonic even if many appends fire many throttles."""
    state, deps = _make_cardkit_fakes()
    ctl = _mk_controller(deps, to="oc_1")

    async def producer(s):
        for i in range(10):
            await s.append(f"chunk-{i:02d} ")
            await asyncio.sleep(0.02)

    await ctl.run(producer)

    seqs = [s for (_c, _e, _txt, s) in state["elem_updates"]]
    assert seqs, "no element updates fired"
    assert seqs == sorted(seqs) and len(set(seqs)) == len(seqs)
    # finish seq strictly greater than every update seq.
    assert state["finishes"][0][1] > max(seqs)


@pytest.mark.asyncio
async def test_markdown_stream_error_appends_footer_then_finishes():
    state, deps = _make_cardkit_fakes()
    ctl = _mk_controller(deps)

    async def producer(s):
        await s.append("some content")
        raise RuntimeError("llm failure")

    with pytest.raises(RuntimeError):
        await ctl.run(producer)

    assert state["elem_updates"], "no element updates fired"
    last_content = state["elem_updates"][-1][2]
    assert "some content" in last_content
    assert "generation interrupted" in last_content
    # Even on error path, finish is still called.
    assert len(state["finishes"]) == 1


# ---- CardStreamController --------------------------------------------------


@pytest.mark.asyncio
async def test_card_stream_update_and_transform_function():
    patched: List[Dict[str, Any]] = []

    async def ensure_created(card):
        return "om_c"

    async def patch_card(mid, card):
        patched.append(card)

    initial = {"body": {"elements": [{"tag": "markdown", "content": "start"}]}}
    ctl = CardStreamController(
        initial=initial,
        ensure_created=ensure_created, patch_card=patch_card,
        min_ms=10, min_chars=1,
    )

    async def producer(s):
        await s.update({"body": {"elements": [{"tag": "markdown", "content": "step 1"}]}})
        await s.update(lambda c: {**c, "body": {"elements": [{"tag": "markdown", "content": "step 2"}]}})

    await ctl.run(producer)
    last = patched[-1]
    assert last["body"]["elements"][0]["content"] == "step 2"


@pytest.mark.asyncio
async def test_card_stream_error_appends_footer_element():
    patched: List[Dict[str, Any]] = []

    async def ensure_created(card):
        return "om_c"

    async def patch_card(mid, card):
        patched.append(card)

    ctl = CardStreamController(
        initial={"body": {"elements": []}},
        ensure_created=ensure_created, patch_card=patch_card,
    )

    async def producer(s):
        await s.update({"body": {"elements": [{"tag": "markdown", "content": "x"}]}})
        raise ValueError("mid-stream fail")

    with pytest.raises(ValueError):
        await ctl.run(producer)
    last_elements = patched[-1]["body"]["elements"]
    assert any("generation interrupted" in (e.get("content") or "") for e in last_elements)
