"""Merge-forward async expansion — single fetch, local traversal.

Pattern:

1. ONE top-level ``fetchSubMessages(messageId)`` call returns the flat list
   of ALL descendants (including deeply-nested merge_forwards).
2. Build a ``parent_id → [children]`` map keyed by ``upper_message_id``.
3. Traverse the tree locally. Nested merge_forward items just recurse into
   the same map — **no additional API calls**.

A naive implementation that re-fetches for each nested merge_forward
multiplies API calls with nesting depth. This module instead matches
node: single fetch, local traversal.

Any failure is captured in the ``.error`` field of the MergeForwardContent —
handlers never see an exception.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

from lark_oapi.core.log import logger

from ..types import (
    MergeForwardContent,
    MergeForwardItem,
    MessageContent,
    UnknownContent,
)
from .registry import parse_message_content


class MergeForwardExpander:
    """Expand a merge_forward message via a single API fetch + local traversal.

    Dependencies are injected so this is easy to test:
        - ``fetch_message(message_id) -> payload dict``: returns the full
          response (expected to contain ``data.items`` — the flat tree).
        - ``resolve_names(open_ids) -> dict[open_id, display_name]``: batch
          name lookup.
    """

    def __init__(
            self,
            fetch_message,
            resolve_names=None,
            max_depth: int = 3,
            max_items: int = 50,
    ):
        self._fetch_message = fetch_message
        self._resolve_names = resolve_names
        self._max_depth = max_depth
        self._max_items = max_items

    async def expand(self, message_id: str, depth: int = 0) -> MergeForwardContent:
        """Fetch once, build map, materialize tree. Never re-fetches."""
        content = MergeForwardContent(loading=False)
        if depth > self._max_depth:
            content.error = "max_depth_exceeded"
            return content

        try:
            payload = await _maybe_await(self._fetch_message(message_id))
        except Exception as e:  # pragma: no cover - network/defensive
            logger.warning("merge_forward fetch failed for %s: %s", message_id, e)
            content.error = f"fetch_failed: {e}"
            return content

        if not payload:
            content.error = "empty_payload"
            return content

        items_raw = _extract_all_items(payload)
        if not items_raw:
            return content  # empty tree — loading=False, items=[]

        children_map = _build_children_map(items_raw, root_id=message_id)

        # One batch name-resolve call for every sender across the whole tree.
        open_ids: Set[str] = set()
        for item in items_raw:
            oid = _get_sender_open_id(item)
            if oid:
                open_ids.add(oid)
        name_map: Dict[str, str] = {}
        if open_ids and self._resolve_names is not None:
            try:
                resolved = await _maybe_await(
                    self._resolve_names(list(open_ids))
                )
                if isinstance(resolved, dict):
                    name_map = {k: v for k, v in resolved.items() if v}
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("merge_forward name resolution failed: %s", e)

        materialized = self._materialize(
            message_id, children_map, name_map, depth=depth
        )
        content.items = materialized.items
        content.truncated = materialized.truncated
        return content

    def _materialize(
            self,
            parent_id: str,
            children_map: Dict[str, List[Dict[str, Any]]],
            name_map: Dict[str, str],
            depth: int,
    ) -> MergeForwardContent:
        """Build one ``MergeForwardContent`` level from the pre-fetched map."""
        result = MergeForwardContent(loading=False)
        if depth > self._max_depth:
            result.error = "max_depth_exceeded"
            return result

        children = children_map.get(parent_id, [])
        if len(children) > self._max_items:
            children = children[: self._max_items]
            result.truncated = True

        items: List[MergeForwardItem] = []
        for item in children:
            try:
                items.append(
                    self._materialize_item(
                        item, children_map, name_map, depth
                    )
                )
            except Exception as e:  # pragma: no cover - defensive
                logger.warning("merge_forward materialize item failed: %s", e)
                continue
        result.items = items
        return result

    def _materialize_item(
            self,
            item: Dict[str, Any],
            children_map: Dict[str, List[Dict[str, Any]]],
            name_map: Dict[str, str],
            depth: int,
    ) -> MergeForwardItem:
        mt = item.get("msg_type") or item.get("message_type") or ""
        oid = _get_sender_open_id(item)
        child_content: MessageContent
        if mt == "merge_forward":
            child_id = item.get("message_id") or ""
            if child_id:
                # Node-aligned: recurse into the SAME map (no new fetch).
                child_content = self._materialize(
                    child_id, children_map, name_map, depth + 1
                )
            else:
                child_content = UnknownContent(message_type="merge_forward", raw=item)
        else:
            body = item.get("body") or item
            raw_content = body.get("content") if isinstance(body, dict) else None
            if raw_content is None:
                raw_content = item.get("content")
            child_content = parse_message_content(mt, raw_content)
        return MergeForwardItem(
            message_id=item.get("message_id") or "",
            sender_open_id=oid,
            sender_name=name_map.get(oid) if oid else None,
            create_time=_as_int(item.get("create_time")),
            content=child_content,
            raw=item,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_all_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return every item dict from the fetch payload — DO NOT filter by msg_type.

    Node traverses the full flat list (including nested merge_forward items)
    and uses ``upper_message_id`` to rebuild the tree; filtering here would
    lose nested children.
    """
    if not isinstance(payload, dict):
        return []
    data = payload.get("data") or payload
    if not isinstance(data, dict):
        return []
    items = data.get("items") or data.get("messages") or []
    if not isinstance(items, list):
        return []
    return [i for i in items if isinstance(i, dict)]


def _build_children_map(
        items: List[Dict[str, Any]], root_id: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Group items by ``upper_message_id`` (fall back to ``root_id``).

    Skips the root item itself to match node's
    ``if (it.message_id === rootId && !it.upper_message_id) continue`` guard.

    Sorts each bucket by ``create_time`` ascending.
    """
    m: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for it in items:
        mid = it.get("message_id")
        upper = it.get("upper_message_id")
        if mid == root_id and not upper:
            continue  # root itself
        parent = upper or root_id
        m[parent].append(it)
    for arr in m.values():
        arr.sort(key=lambda x: _as_int(x.get("create_time")) or 0)
    return dict(m)


def _get_sender_open_id(item: Dict[str, Any]) -> Optional[str]:
    sender = item.get("sender") or {}
    if isinstance(sender, dict):
        return (
            sender.get("id")
            or sender.get("open_id")
            or (sender.get("sender_id") or {}).get("open_id")
            if isinstance(sender.get("sender_id"), dict)
            else sender.get("id") or sender.get("open_id")
        )
    return None


def _as_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


async def _maybe_await(v):
    import inspect

    if inspect.isawaitable(v):
        return await v
    return v
