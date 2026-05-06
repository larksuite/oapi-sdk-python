"""Converter: PostContent → Markdown (headings / bold / italic / code / links)."""

from typing import Any, Dict, List, Tuple

from ...types import PostContent, ResourceDescriptor


def convert(content: PostContent) -> Tuple[str, List[ResourceDescriptor]]:
    md = _post_to_markdown(content.post) if content.post else content.text
    return md, []


def _post_to_markdown(post: Dict[str, Any]) -> str:
    if not isinstance(post, dict) or not post:
        return ""
    locale = next(iter(post.values()))
    if not isinstance(locale, dict):
        return ""
    lines: List[str] = []
    title = locale.get("title")
    if title:
        lines.append(f"# {title}")
    for para in locale.get("content") or []:
        chunks: List[str] = []
        for el in para or []:
            if not isinstance(el, dict):
                continue
            tag = el.get("tag")
            if tag == "text":
                t = el.get("text") or ""
                styles = el.get("style") or []
                if "bold" in styles:
                    t = f"**{t}**"
                if "italic" in styles:
                    t = f"*{t}*"
                if "code" in styles:
                    t = f"`{t}`"
                if "strikethrough" in styles:
                    t = f"~~{t}~~"
                chunks.append(t)
            elif tag == "a":
                chunks.append(f"[{el.get('text') or ''}]({el.get('href') or ''})")
            elif tag == "at":
                nm = el.get("user_name") or el.get("user_id") or ""
                chunks.append(f"@{nm}")
            elif tag == "emotion":
                chunks.append(f":{el.get('emoji_type') or ''}:")
            elif tag == "img":
                chunks.append(f"![image]({el.get('image_key') or ''})")
            elif tag == "media":
                chunks.append(f"[media:{el.get('file_key') or ''}]")
            elif tag == "code_block":
                lang = (el.get("language") or "").lower()
                text = el.get("text") or ""
                chunks.append(f"```{lang}\n{text}\n```")
            elif tag == "hr":
                chunks.append("---")
            elif tag == "md":
                chunks.append(el.get("text") or "")
        line = "".join(chunks)
        if line:
            lines.append(line)
    return "\n\n".join(lines).strip()
