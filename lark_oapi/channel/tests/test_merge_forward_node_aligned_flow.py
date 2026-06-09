"""Regression: merge_forward expands in ONE fetch + local tree traversal.

Covers the alignment fix that replaced per-nested-forward re-fetching with
node-sdk's ``buildChildrenMap``/``formatSubTree`` pattern (commit ccc7e31's
channel/normalize/converters/merge-forward.ts).

The invariant this file protects: no matter how deeply nested the forward
tree, ``expand()`` performs exactly ONE ``fetch_message`` call. Nested
forwards are materialized from the same flat items list via
``upper_message_id`` parent links.
"""

import json

import pytest

from lark_oapi.channel.normalize.merge_forward import MergeForwardExpander
from lark_oapi.channel.types import (
    MergeForwardContent,
    TextContent,
)


def _child(mid, text, upper=None, sender_id="ou_a"):
    it = {
        "message_id": mid,
        "msg_type": "text",
        "body": {"content": json.dumps({"text": text})},
        "sender": {"id": sender_id},
        "create_time": "100",
    }
    if upper:
        it["upper_message_id"] = upper
    return it


def _nested_mf(mid, upper=None):
    it = {
        "message_id": mid,
        "msg_type": "merge_forward",
        "body": {"content": "{}"},
        "sender": {"id": "ou_x"},
        "create_time": "50",
    }
    if upper:
        it["upper_message_id"] = upper
    return it


@pytest.mark.asyncio
async def test_single_fetch_for_deeply_nested_tree():
    """Even with 3 levels of nested merge_forward, ``expand()`` fetches once."""
    fetch_calls = []

    async def fetch(mid):
        fetch_calls.append(mid)
        # Flat list: root → mf_l1 → mf_l2 → text leaf.
        return {"data": {"items": [
            {"message_id": "root", "msg_type": "merge_forward", "body": {"content": "{}"}},
            _nested_mf("mf_l1", upper="root"),
            _nested_mf("mf_l2", upper="mf_l1"),
            _child("leaf", "deep hello", upper="mf_l2"),
        ]}}

    exp = MergeForwardExpander(fetch_message=fetch)
    res = await exp.expand("root")

    # Exactly ONE fetch — critical divergence from the pre-fix behavior.
    assert fetch_calls == ["root"], f"expected 1 fetch, got {fetch_calls}"

    # Tree shape: root has 1 child (mf_l1), which has 1 child (mf_l2), which has leaf.
    assert len(res.items) == 1
    lvl1 = res.items[0].content
    assert isinstance(lvl1, MergeForwardContent)
    assert len(lvl1.items) == 1
    lvl2 = lvl1.items[0].content
    assert isinstance(lvl2, MergeForwardContent)
    assert len(lvl2.items) == 1
    leaf = lvl2.items[0].content
    assert isinstance(leaf, TextContent)
    assert leaf.text == "deep hello"


@pytest.mark.asyncio
async def test_items_without_upper_message_id_default_to_root_parent():
    """Legacy payloads (no upper_message_id) still work — items attach to root."""

    async def fetch(mid):
        return {"data": {"items": [
            {"message_id": mid, "msg_type": "merge_forward", "body": {"content": "{}"}},
            _child("c1", "hello"),
            _child("c2", "world", sender_id="ou_b"),
        ]}}

    exp = MergeForwardExpander(fetch_message=fetch)
    res = await exp.expand("om_root")
    assert len(res.items) == 2
    assert isinstance(res.items[0].content, TextContent)
    assert res.items[0].content.text == "hello"


@pytest.mark.asyncio
async def test_sender_names_batched_once_for_whole_tree():
    """All sender open_ids across depths should be batch-resolved in one call."""
    batch_calls = []

    async def fetch(mid):
        return {"data": {"items": [
            {"message_id": "root", "msg_type": "merge_forward", "body": {"content": "{}"}},
            _nested_mf("mf_l1", upper="root"),
            _child("c_top", "top", upper="root", sender_id="ou_top"),
            _child("c_nested_1", "n1", upper="mf_l1", sender_id="ou_n1"),
            _child("c_nested_2", "n2", upper="mf_l1", sender_id="ou_n2"),
        ]}}

    async def names(ids):
        batch_calls.append(sorted(ids))
        return {i: f"Name-{i}" for i in ids}

    exp = MergeForwardExpander(fetch_message=fetch, resolve_names=names)
    res = await exp.expand("root")

    assert len(batch_calls) == 1
    ids = batch_calls[0]
    assert "ou_top" in ids and "ou_n1" in ids and "ou_n2" in ids and "ou_x" in ids
    # Names applied to both the top item and items inside the nested forward.
    top_item = next(it for it in res.items if it.sender_open_id == "ou_top")
    assert top_item.sender_name == "Name-ou_top"
    nested_content = next(
        it for it in res.items if isinstance(it.content, MergeForwardContent)
    ).content
    nested_names = {i.sender_name for i in nested_content.items}
    assert nested_names == {"Name-ou_n1", "Name-ou_n2"}


@pytest.mark.asyncio
async def test_placeholder_in_nested_child_resolves_via_top_mentions():
    """Node resolves ``@_user_N`` found in forwarded child content against the
    OUTER message's mentions map (via the single-pass ``resolveMentions`` on the
    final rendered text). Python's pipeline mirrors this with a second-pass
    ``resolve_mentions`` on ``flat_text`` — this test pins that behavior.
    """
    # Build a fake message_event shape the pipeline accepts. Child text
    # contains a @_user_1 placeholder; outer mentions array carries the entry.
    from types import SimpleNamespace

    from lark_oapi.channel.normalize.pipeline import (
        InboundPipeline,
        PipelineConfig,
        PipelineDeps,
    )

    async def fetch_message(mid):
        # The outer merge_forward root + one child whose text has a placeholder.
        return {"data": {"items": [
            {"message_id": "om_root", "msg_type": "merge_forward", "body": {"content": "{}"}},
            _child("c_placeholder", "ping @_user_1 wake up", upper="om_root"),
        ]}}

    cfg = PipelineConfig()
    cfg.inbound.expand_merge_forward = True
    deps = PipelineDeps(fetch_message=fetch_message)
    pipe = InboundPipeline(cfg=cfg, deps=deps)

    message_event = SimpleNamespace(
        message_id="om_root",
        root_id="",
        parent_id="",
        create_time="0",
        chat_id="oc_1",
        thread_id=None,
        chat_type="group",
        message_type="merge_forward",
        content="{}",
        mentions=[
            {"key": "@_user_1", "id": {"open_id": "ou_alice"}, "name": "Alice"},
        ],
        user_agent=None,
    )
    sender = SimpleNamespace(
        sender_id=SimpleNamespace(open_id="ou_sender", user_id=None, union_id=None),
        sender_type="user",
    )
    inbound = await pipe.process(
        event_id="e1", message_event=message_event, sender=sender,
    )
    assert inbound is not None
    # Placeholder inside the forwarded child text must be resolved to @Alice.
    assert "@Alice" in inbound.content_text
    assert "@_user_1" not in inbound.content_text
