"""Converter: PostContent → Markdown (headings / bold / italic / code / links)."""

from typing import Any, Dict, List, Tuple

from ...types import PostContent, ResourceDescriptor
from ._utils import attr


def convert(content: PostContent) -> Tuple[str, List[ResourceDescriptor]]:
    md = _post_to_markdown(content.post) if content.post else content.text
    resources = _post_resources(content.post) if content.post else []
    return md, resources


def _attachment_files(post: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Top-level attachment zone (``files`` array) of a post message.

    The rich-text attachment zone lives at the top level of the post JSON,
    outside any locale document: ``files: [{file_key, file_name, is_folder}]``.
    Standalone file/folder tags are rendered the same way as the file/folder
    message converters (``<file key="..." name="..."/>`` / ``<folder .../>``).
    """
    if not isinstance(post, dict):
        return []
    files = post.get("files")
    if not isinstance(files, list):
        return []
    return [f for f in files if isinstance(f, dict) and isinstance(f.get("file_key"), str) and f["file_key"]]


def _iter_documents(post: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(post, dict) or not post:
        return []
    if "content" in post:
        return [post]
    return [doc for doc in post.values() if isinstance(doc, dict)]


def _post_to_markdown(post: Dict[str, Any]) -> str:
    docs = _iter_documents(post)
    if not docs:
        return ""
    locale = docs[0]
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
    for f in _attachment_files(post):
        key = f["file_key"]
        name = f.get("file_name") or ""
        if f.get("is_folder"):
            if name:
                lines.append(f'<folder key="{key}" name="{attr(name)}"/>')
            else:
                lines.append(f'<folder key="{key}"/>')
        else:
            if name:
                lines.append(f'<file key="{key}" name="{attr(name)}"/>')
            else:
                lines.append(f'<file key="{key}"/>')
    return "\n\n".join(lines).strip()


def _post_resources(post: Dict[str, Any]) -> List[ResourceDescriptor]:
    resources: List[ResourceDescriptor] = []
    seen = set()

    def add(kind: str, key: Any, *, file_name: Any = None) -> None:
        if not isinstance(key, str) or not key:
            return
        dedup_key = (kind, key)
        if dedup_key in seen:
            return
        seen.add(dedup_key)
        resources.append(
            ResourceDescriptor(
                type=kind,  # type: ignore[arg-type]
                file_key=key,
                file_name=file_name if isinstance(file_name, str) and file_name else None,
            )
        )

    for doc in _iter_documents(post):
        for para in doc.get("content") or []:
            for el in para or []:
                if not isinstance(el, dict):
                    continue
                tag = el.get("tag")
                if tag == "img":
                    add("image", el.get("image_key"))
                elif tag == "media":
                    add("video", el.get("file_key"))
                elif tag == "audio":
                    add("audio", el.get("file_key"))
                elif tag == "file":
                    add("file", el.get("file_key"), file_name=el.get("file_name"))
    # Attachment zone: files are downloadable resources; folders are rendered
    # as tags only (mirrors the standalone folder converter, resources=[]).
    for f in _attachment_files(post):
        if f.get("is_folder"):
            continue
        add("file", f.get("file_key"), file_name=f.get("file_name"))
    return resources
