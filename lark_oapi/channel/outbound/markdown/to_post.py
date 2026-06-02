"""Markdown → Lark post-AST converter.

Covers the common subset: headings, bold, italic, inline code, code blocks,
links, bullet / numbered lists, blockquotes, <at>, and horizontal rules.
Unsupported syntax falls back to plain text, preserving readability.

This is a pragmatic converter — not a full CommonMark parser — because the
Lark post AST only supports a limited vocabulary. Lines that don't match a
recognized pattern are emitted as single `text` runs with inline markers
stripped.
"""

import re
from typing import Any, Dict, List, Tuple

from ...types import Identity

# Inline marker patterns (order matters: most specific first).
# Italic is tricky because `**bold**` also matches `*...*`. We require that
# the italic delimiter is not adjacent to another `*` (or `_`).
_INLINE_PATTERNS = [
    (re.compile(r"\*\*(.+?)\*\*"), "bold"),
    (re.compile(r"__(.+?)__"), "bold"),
    (re.compile(r"(?<!\*)\*(?!\*)(?!\s)([^*\n]+?)(?<!\s)\*(?!\*)"), "italic"),
    (re.compile(r"(?<!\w)(?<!_)_(?!_)(?!\s)([^_\n]+?)(?<!\s)_(?!_)(?!\w)"), "italic"),
    (re.compile(r"`([^`\n]+)`"), "code"),
    (re.compile(r"~~(.+?)~~"), "strikethrough"),
]
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_AT_RE = re.compile(r"<at\s+([^>]+)>([^<]*)</at>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([\w_-]+)\s*=\s*"([^"]*)"')


def _parse_inline_runs(line: str) -> List[Dict[str, Any]]:
    """Return list of text runs with style attributes for a single line."""
    if not line:
        return []

    # Collect disjoint match ranges (bold / italic / code / link / at),
    # non-overlapping, leftmost-first. Whatever is left is plain text.
    matches: List[Tuple[int, int, Dict[str, Any]]] = []

    for pat, style in _INLINE_PATTERNS:
        for m in pat.finditer(line):
            matches.append((m.start(), m.end(), {"tag": "text", "text": m.group(1), "style": [style]}))

    for m in _LINK_RE.finditer(line):
        matches.append((m.start(), m.end(), {"tag": "a", "text": m.group(1), "href": m.group(2)}))

    for m in _AT_RE.finditer(line):
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        uid = attrs.get("user_id") or attrs.get("open_id") or ""
        name = m.group(2) or attrs.get("user_name") or uid
        node: Dict[str, Any] = {"tag": "at"}
        if uid:
            node["user_id"] = uid
        if name:
            node["user_name"] = name
        matches.append((m.start(), m.end(), node))

    matches.sort(key=lambda t: (t[0], t[1]))
    # Remove overlapping matches (keep the earliest; drop overlaps).
    filtered: List[Tuple[int, int, Dict[str, Any]]] = []
    cursor = 0
    for s, e, node in matches:
        if s < cursor:
            continue
        filtered.append((s, e, node))
        cursor = e

    # Interleave with plain-text runs.
    out: List[Dict[str, Any]] = []
    pos = 0
    for s, e, node in filtered:
        if s > pos:
            out.append({"tag": "text", "text": line[pos:s]})
        out.append(node)
        pos = e
    if pos < len(line):
        out.append({"tag": "text", "text": line[pos:]})
    return [r for r in out if r.get("text") or r.get("tag") == "at" or r.get("tag") == "a"]


def _plain(text: str) -> List[Dict[str, Any]]:
    return [{"tag": "text", "text": text}] if text else []


def markdown_to_post_ast(
        md: str,
        title: str = "",
        locale: str = "zh_cn",
        mentions: "list[Identity] | None" = None,
        table_mode: str = "off",
        tag_md_mode: str = "structured",
) -> Dict[str, Any]:
    """Produce a Lark post AST (`{locale: {title, content: [[...]]}}`) from Markdown.

    Mentions supplied via `mentions` are appended (inline @tags) to the first
    paragraph so the recipient actually gets notified.

    ``tag_md_mode``:
        - ``"structured"`` (default): parse Markdown into explicit post nodes
          (``tag:text`` with style attributes, ``tag:a`` for links,
          ``tag:code_block`` for fenced code, etc). Cross-client deterministic.
        - ``"native"``: wrap the raw markdown into one or more ``tag:md`` rows
          (split at code-fence boundaries) and let the Feishu client's own
          markdown parser render natively. Renders headers/blockquotes/lists
          with native styling, but rendering depends on Feishu client version.
    """
    if tag_md_mode == "native":
        return _build_native_md_ast(md, title=title, locale=locale, mentions=mentions)
    lines = (md or "").splitlines()
    paragraphs: List[List[Dict[str, Any]]] = []

    i = 0
    n = len(lines)

    def _flush_paragraph(buf: List[str]) -> None:
        if not buf:
            return
        para_text = "\n".join(buf).strip()
        if not para_text:
            return
        paragraphs.append(_parse_inline_runs(para_text))
        buf.clear()

    buf: List[str] = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Horizontal rule
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped or ""):
            _flush_paragraph(buf)
            paragraphs.append([{"tag": "hr"}])
            i += 1
            continue

        # ATX heading #
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            _flush_paragraph(buf)
            heading_text = m.group(2).strip()
            run = _parse_inline_runs(heading_text)
            for r in run:
                if r.get("tag") == "text":
                    styles = r.setdefault("style", [])
                    if "bold" not in styles:
                        styles.append("bold")
            paragraphs.append(run or _plain(heading_text))
            i += 1
            continue

        # Fenced code block
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            _flush_paragraph(buf)
            lang = m.group(1) or ""
            code_lines: List[str] = []
            i += 1
            while i < n and not re.match(r"^```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1  # skip closing fence
            paragraphs.append(
                [
                    {
                        "tag": "code_block",
                        "language": lang.upper() if lang else "TEXT",
                        "text": "\n".join(code_lines),
                    }
                ]
            )
            continue

        # Blockquote
        if stripped.startswith(">"):
            _flush_paragraph(buf)
            quote_lines: List[str] = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            quote_text = "\n".join(quote_lines)
            run = _parse_inline_runs(quote_text)
            # Lark post has no native blockquote; prefix each line with │ so it's
            # visually distinguishable.
            paragraphs.append([{"tag": "text", "text": "│ "}] + run)
            continue

        # Bullet list / ordered list: emit each bullet as its own paragraph.
        if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            _flush_paragraph(buf)
            while i < n and (
                    re.match(r"^\s*[-*+]\s+", lines[i])
                    or re.match(r"^\s*\d+[.)]\s+", lines[i])
            ):
                item_line = lines[i]
                bullet_text = re.sub(r"^\s*[-*+]\s+", "• ", item_line)
                bullet_text = re.sub(r"^\s*\d+[.)]\s+", "\\g<0>", bullet_text)
                paragraphs.append(_parse_inline_runs(bullet_text))
                i += 1
            continue

        # Table: depend on table_mode setting.
        if _looks_like_table_row(line):
            _flush_paragraph(buf)
            table_lines: List[str] = [line]
            i += 1
            while i < n and _looks_like_table_row(lines[i]):
                table_lines.append(lines[i])
                i += 1
            converted = _convert_table(table_lines, mode=table_mode)
            paragraphs.extend(converted)
            continue

        if not stripped:
            _flush_paragraph(buf)
            i += 1
            continue

        buf.append(line)
        i += 1

    _flush_paragraph(buf)

    # Inject @mentions at the start of the first paragraph so recipients are
    # notified.
    if mentions and paragraphs:
        at_runs: List[Dict[str, Any]] = []
        for ident in mentions:
            if not ident or not ident.open_id:
                continue
            at_runs.append(
                {
                    "tag": "at",
                    "user_id": ident.open_id,
                    "user_name": ident.display_name or "",
                }
            )
            at_runs.append({"tag": "text", "text": " "})
        paragraphs[0] = at_runs + paragraphs[0]

    if not paragraphs:
        paragraphs = [_plain("")]

    return {locale: {"title": title or "", "content": paragraphs}}


def _looks_like_table_row(line: str) -> bool:
    stripped = (line or "").strip()
    return stripped.count("|") >= 2 and stripped.startswith("|") and stripped.endswith("|")


def _convert_table(lines: List[str], mode: str) -> List[List[Dict[str, Any]]]:
    """Convert a Markdown table into paragraphs based on `mode`."""
    if mode == "off":
        return [_parse_inline_runs(ln) for ln in lines]

    # Drop the separator row (---|---).
    rows = [
        [c.strip() for c in ln.strip().strip("|").split("|")]
        for ln in lines
        if not re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", ln)
    ]
    if not rows:
        return [_parse_inline_runs(ln) for ln in lines]

    if mode == "bullets":
        # "col1: val1 · col2: val2" per row, excluding the header row.
        header = rows[0]
        out: List[List[Dict[str, Any]]] = []
        for row in rows[1:]:
            pairs = [f"{header[i] if i < len(header) else ''}: {c}" for i, c in enumerate(row)]
            out.append([{"tag": "text", "text": "• " + " · ".join(pairs)}])
        return out or [_parse_inline_runs(lines[0])]

    if mode == "code":
        src = "\n".join(lines)
        return [[{"tag": "code_block", "language": "TEXT", "text": src}]]

    # mode == "table"
    if mode == "table":
        rendered = []
        for row in rows:
            rendered.append([{"tag": "text", "text": " | ".join(row)}])
        return rendered

    # default fallback
    return [_parse_inline_runs(ln) for ln in lines]


_FENCE_LINE_RE = re.compile(r"^```")


def _build_native_md_ast(
        md: str,
        title: str = "",
        locale: str = "zh_cn",
        mentions: "list[Identity] | None" = None,
) -> Dict[str, Any]:
    """Pack raw markdown into one or more ``tag:md`` rows.

    Each fenced code block is its own row; prose between fences is its own
    row. This mirrors known Feishu client behavior (md content immediately
    after a code fence may be swallowed otherwise).

    Mentions are attached to the first row (consistent with structured mode).
    """
    segments = _split_at_code_fences(md or "")
    rows: List[List[Dict[str, Any]]] = [
        [{"tag": "md", "text": seg}] for seg in segments
    ]

    if mentions and rows:
        at_runs: List[Dict[str, Any]] = []
        for ident in mentions:
            if not ident or not ident.open_id:
                continue
            at_runs.append({
                "tag": "at",
                "user_id": ident.open_id,
                "user_name": ident.display_name or "",
            })
            at_runs.append({"tag": "text", "text": " "})
        rows[0] = at_runs + rows[0]

    return {locale: {"title": title or "", "content": rows}}


def _split_at_code_fences(text: str) -> List[str]:
    """Split markdown at fenced-code-block boundaries.

    Returns a list of non-empty segments where each segment is either a
    prose block (no fence lines) or one complete fenced code block
    (open fence + body + close fence). Unclosed fences are absorbed into
    the trailing segment as-is — no content is dropped.

    Distinct from ``splitter.split_with_code_fences``: this one is
    length-agnostic and never inserts synthetic close/reopen fences.
    """
    if not text:
        return []
    lines = text.split("\n")
    out: List[str] = []
    buf: List[str] = []
    in_fence = False

    def _flush():
        if buf:
            out.append("\n".join(buf))
            buf.clear()

    for line in lines:
        is_fence = bool(_FENCE_LINE_RE.match(line))
        if not in_fence and is_fence:
            # Closing prose, opening fence
            _flush()
            buf.append(line)
            in_fence = True
        elif in_fence and is_fence:
            # Closing fence
            buf.append(line)
            _flush()
            in_fence = False
        else:
            buf.append(line)

    _flush()
    return [s for s in out if s != ""]
