"""Converter: InteractiveContent — deep-walk a CardKit v2 card.

Concatenates markdown / plain-text leaves in traversal order, deduping
adjacent duplicates. Unknown widgets are skipped.
"""

from typing import Any, Dict, List, Tuple

from ...types import InteractiveContent, ResourceDescriptor


def convert(content: InteractiveContent) -> Tuple[str, List[ResourceDescriptor]]:
    return _walk(content.card), []


def _walk(card: Dict[str, Any]) -> str:
    if not isinstance(card, dict):
        return "[interactive]"
    seen: List[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            tag = node.get("tag")
            if tag == "markdown":
                c = node.get("content")
                if c:
                    seen.append(str(c))
                return
            if tag == "plain_text":
                c = node.get("content")
                if c:
                    seen.append(str(c))
                return
            if tag == "div":
                text = node.get("text")
                if isinstance(text, dict):
                    visit(text)
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    header = card.get("header") or {}
    if isinstance(header, dict):
        visit(header.get("title"))
        visit(header.get("subtitle"))
    body = card.get("body") or {}
    visit(body)

    deduped: List[str] = []
    for s in seen:
        s = s.strip()
        if not s:
            continue
        if deduped and deduped[-1] == s:
            continue
        deduped.append(s)
    return "\n".join(deduped) or "[interactive]"
