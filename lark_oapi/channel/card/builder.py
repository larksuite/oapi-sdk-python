"""CardKit v2 builder — fluent chain to compose interactive cards.

Common elements are typed; `.raw()` provides an escape hatch for JSON not
covered by the builder methods.
"""

import re
from copy import deepcopy
from typing import Any, Dict, List, Optional

from ..types import CardPayload

# Cell values containing these constructs should be rendered via `lark_md`
# so bold/italic/code/link stay formatted; plain cells use `text`.
_INLINE_MD_IN_CELL_RE = re.compile(
    r"(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*)|(`[^`\n]+`)|(\[[^\]]+\]\([^)]+\))"
)

HeaderTemplate = str  # 'blue' | 'red' | 'green' | ...


class CardBuilder:
    """Fluent v2 card builder.

    Example:
        >>> c = (new_card()
        ...     .header(title="Deploy", template="blue")
        ...     .markdown("Running **step 2**")
        ...     .divider()
        ...     .button(label="Approve", action={"type": "approve"}, style="primary")
        ...     .build())
    """

    def __init__(self) -> None:
        self._header: Optional[Dict[str, Any]] = None
        self._body_elements: List[Dict[str, Any]] = []
        self._config: Dict[str, Any] = {}
        self._variables: Dict[str, Any] = {}
        self._streaming: bool = False

    # ---- meta -----------------------------------------------------------------
    def streaming(self, enabled: bool = True) -> "CardBuilder":
        """Mark this card for use with the streaming card helpers."""
        self._streaming = enabled
        return self

    def config(self, **kwargs: Any) -> "CardBuilder":
        self._config.update(kwargs)
        return self

    def variable(self, name: str, value: Any) -> "CardBuilder":
        self._variables[name] = value
        return self

    # ---- header ---------------------------------------------------------------
    def header(
            self,
            title: str,
            *,
            subtitle: Optional[str] = None,
            template: HeaderTemplate = "blue",
            icon: Optional[Dict[str, Any]] = None,
    ) -> "CardBuilder":
        h: Dict[str, Any] = {"title": {"tag": "plain_text", "content": title}}
        if subtitle:
            h["subtitle"] = {"tag": "plain_text", "content": subtitle}
        if template:
            h["template"] = template
        if icon:
            h["icon"] = icon
        self._header = h
        return self

    # ---- body element helpers ------------------------------------------------
    def markdown(self, content: str) -> "CardBuilder":
        self._body_elements.append({"tag": "markdown", "content": content})
        return self

    def text(self, content: str) -> "CardBuilder":
        self._body_elements.append(
            {"tag": "div", "text": {"tag": "plain_text", "content": content}}
        )
        return self

    def divider(self) -> "CardBuilder":
        self._body_elements.append({"tag": "hr"})
        return self

    def image(self, img_key: str, *, alt: Optional[str] = None, title: Optional[str] = None) -> "CardBuilder":
        el: Dict[str, Any] = {"tag": "img", "img_key": img_key}
        if alt:
            el["alt"] = {"tag": "plain_text", "content": alt}
        if title:
            el["title"] = {"tag": "plain_text", "content": title}
        self._body_elements.append(el)
        return self

    def note(self, elements: List[Dict[str, Any]]) -> "CardBuilder":
        """Emit a subtle-styled line.

        The v1 `note` tag is gone in CardKit v2; we flatten plain_text children
        into a single grey markdown line so existing builder chains keep working.
        """
        if isinstance(elements, list):
            parts = []
            for el in elements:
                if isinstance(el, dict) and el.get("tag") == "plain_text":
                    parts.append(el.get("content", ""))
                elif isinstance(el, dict):
                    parts.append(el.get("content", "") or el.get("text", ""))
                else:
                    parts.append(str(el))
            text = " · ".join(p for p in parts if p)
        else:
            text = str(elements)
        self._body_elements.append(
            {"tag": "markdown", "content": f"<font color='grey'>{text}</font>"}
        )
        return self

    def code_block(self, content: str, language: str = "text") -> "CardBuilder":
        self._body_elements.append(
            {
                "tag": "markdown",
                "content": f"```{language}\n{content}\n```",
            }
        )
        return self

    # ---- interactive elements -----------------------------------------------
    # CardKit v2 note: the `action` container tag from v1 is gone. Interactive
    # widgets (button / select_static / etc.) are emitted as top-level body
    # elements; multiple buttons on one row use `column_set`.

    def _build_button(
            self,
            *,
            label: str,
            action: Optional[Dict[str, Any]] = None,
            style: str = "default",
            url: Optional[str] = None,
            confirm: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        btn: Dict[str, Any] = {
            "tag": "button",
            "text": {"tag": "plain_text", "content": label},
            "type": style,
        }
        if url:
            btn["url"] = url
        if action is not None:
            btn["value"] = action
        if confirm:
            btn["confirm"] = confirm
        return btn

    def button(
            self,
            label: str,
            *,
            action: Optional[Dict[str, Any]] = None,
            style: str = "default",
            url: Optional[str] = None,
            confirm: Optional[Dict[str, Any]] = None,
    ) -> "CardBuilder":
        self._body_elements.append(
            self._build_button(label=label, action=action, style=style, url=url, confirm=confirm)
        )
        return self

    def buttons(self, items: List[Dict[str, Any]]) -> "CardBuilder":
        """Render several buttons in one horizontal row via column_set.

        Each item uses `button`-style keys: label, action, style, url, confirm.
        """
        cols: List[Dict[str, Any]] = []
        for it in items:
            btn = self._build_button(
                label=it.get("label", ""),
                action=it.get("action"),
                style=it.get("style", "default"),
                url=it.get("url"),
                confirm=it.get("confirm"),
            )
            cols.append({"tag": "column", "elements": [btn]})
        self._body_elements.append({"tag": "column_set", "columns": cols})
        return self

    def select(
            self,
            placeholder: str,
            *,
            options: List[Dict[str, str]],
            action: Optional[Dict[str, Any]] = None,
    ) -> "CardBuilder":
        sel: Dict[str, Any] = {
            "tag": "select_static",
            "placeholder": {"tag": "plain_text", "content": placeholder},
            "options": [
                {
                    "text": {"tag": "plain_text", "content": o.get("label", "")},
                    "value": o.get("value", ""),
                }
                for o in options
            ],
        }
        if action is not None:
            sel["value"] = action
        self._body_elements.append(sel)
        return self

    def column_set(self, columns: List["CardBuilder"]) -> "CardBuilder":
        """Emit a column_set whose sub-columns are themselves built via CardBuilder.

        Only the body elements of each sub-builder are embedded (header and
        streaming flags on sub-columns are ignored).
        """
        cols = [{"tag": "column", "elements": c._body_elements} for c in columns]
        self._body_elements.append({"tag": "column_set", "columns": cols})
        return self

    def table(
            self,
            headers: List[str],
            rows: List[List[str]],
            *,
            page_size: int = 5,
            data_types: Optional[List[str]] = None,
    ) -> "CardBuilder":
        """Append a native Card 2.0 ``table`` component.

        Emits the structured ``{"tag": "table", "columns": [...], "rows": [...]}``
        element — **not** a GFM pipe-table stuffed into a markdown element.
        Feishu's ``markdown`` and post ``md`` tags silently drop pipe-table
        syntax, so the old string-based rendering showed as raw pipes or
        blank messages. Use ``.raw({...})`` only if you need fields beyond
        what this signature covers.

        ``data_types`` overrides the per-column auto-detection. When omitted,
        columns whose cells contain inline markdown (bold / italic / inline
        code / link) pick ``lark_md``; plain columns pick ``text``.
        ``page_size`` is clamped to Feishu's 1-10 range.
        """
        normalized_rows: List[List[str]] = []
        for row in rows:
            cells = [str(c) if c is not None else "" for c in row]
            while len(cells) < len(headers):
                cells.append("")
            normalized_rows.append(cells[: len(headers)])

        if data_types is not None and len(data_types) != len(headers):
            raise ValueError(
                "data_types length must match headers length"
            )

        columns: List[Dict[str, Any]] = []
        for idx, header in enumerate(headers):
            if data_types is not None:
                data_type = data_types[idx]
            else:
                column_cells = (row[idx] for row in normalized_rows)
                data_type = (
                    "lark_md"
                    if any(_INLINE_MD_IN_CELL_RE.search(c) for c in column_cells)
                    else "text"
                )
            columns.append({
                "name": f"col_{idx}",
                "display_name": header,
                "data_type": data_type,
            })

        rows_data = [
            {f"col_{idx}": cell for idx, cell in enumerate(row)}
            for row in normalized_rows
        ]

        self._body_elements.append({
            "tag": "table",
            "page_size": max(1, min(10, page_size)),
            "columns": columns,
            "rows": rows_data,
        })
        return self

    def progress(self, percent: int, *, label: Optional[str] = None) -> "CardBuilder":
        percent = max(0, min(100, percent))
        bar = "▓" * (percent // 5) + "░" * (20 - percent // 5)
        md = f"`{bar}`  **{percent}%**"
        if label:
            md = f"{label}\n{md}"
        return self.markdown(md)

    def footer(self, text: str) -> "CardBuilder":
        self._body_elements.append(
            {"tag": "markdown", "content": f"<font color='grey'>{text}</font>"}
        )
        return self

    # ---- escape hatch --------------------------------------------------------
    def raw(self, element: Dict[str, Any]) -> "CardBuilder":
        self._body_elements.append(element)
        return self

    # ---- build ---------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        card_dict: Dict[str, Any] = {
            "schema": "2.0",
            "config": dict(self._config),
            "body": {"elements": list(self._body_elements)},
        }
        if self._streaming:
            card_dict["config"]["streaming_mode"] = True
            card_dict["config"]["summary"] = {"content": ""}
        if self._header is not None:
            card_dict["header"] = deepcopy(self._header)
        if self._variables:
            card_dict["variables"] = dict(self._variables)
        return card_dict

    def build(self) -> CardPayload:
        return CardPayload(data=self.to_dict(), version="v2")


def new_card() -> CardBuilder:
    """Factory helper: return a fresh :class:`CardBuilder`.

    Prefer ``new_card()`` over instantiating ``CardBuilder()`` directly — the
    name documents intent and matches TypeScript's ``lark.newCard()``.
    """
    return CardBuilder()


# Back-compat alias; scheduled for removal after 2.0.
card = new_card
