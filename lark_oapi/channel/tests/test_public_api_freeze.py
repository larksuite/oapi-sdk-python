"""Public-API freeze tests for the dedup contract.

Locks the DedupStore Protocol signature and the helper exports so that the
contract documented to consumers (Hermes JsonFileDedupStore et al.) cannot
silently drift.
"""

import ast
import inspect
import re
from pathlib import Path

import pytest

from lark_oapi.channel import DedupStore, InMemoryDedupStore
from lark_oapi.channel import make_event_key, make_message_key
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler

ROOT = Path(__file__).resolve().parents[3]


def test_dedup_store_protocol_methods_frozen():
    """DedupStore must expose seen(key) and mark(key, ttl_seconds) — no rename."""
    # seen(key) -> bool
    sig = inspect.signature(DedupStore.seen)
    assert list(sig.parameters.keys()) == ["self", "key"]

    # mark(key, ttl_seconds) -> None
    sig = inspect.signature(DedupStore.mark)
    assert list(sig.parameters.keys()) == ["self", "key", "ttl_seconds"]


def test_in_memory_dedup_store_implements_protocol():
    """The in-memory reference impl must satisfy the Protocol at runtime."""
    store = InMemoryDedupStore()
    assert isinstance(store, DedupStore)
    assert store.seen("anything") is False
    store.mark("k1", ttl_seconds=60)
    assert store.seen("k1") is True


def test_make_event_key_format():
    """Event-keyer must produce stable `evt:<account>:<event_id>` form."""
    assert make_event_key("acc1", "evt1") == "evt:acc1:evt1"


def test_make_message_key_format():
    """Message-keyer must produce stable `msg:<account>:<message_id>` form."""
    assert make_message_key("acc1", "msg1") == "msg:acc1:msg1"


def test_do_without_validation_public_alias_delegates_with_deprecation(monkeypatch):
    """Keep the old public method as a deprecated compatibility shim."""
    handler = EventDispatcherHandler()
    calls = []

    def fake_dispatch(payload):
        calls.append(payload)
        return {"ok": True}

    monkeypatch.setattr(handler, "_do_without_validation", fake_dispatch)

    with pytest.warns(DeprecationWarning, match="do_without_validation"):
        result = handler.do_without_validation(b'{"schema":"2.0"}')

    assert result == {"ok": True}
    assert calls == [b'{"schema":"2.0"}']


def test_readme_links_channel_docs_and_samples_instead_of_tests():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "lark_oapi/channel/tests/" not in readme
    assert "docs/channel/" not in readme
    assert "doc/channel/quickstart.md" in readme
    assert "doc/channel/reference.md" in readme
    assert "samples/channel/echo_bot.py" in readme
    assert "/blob/v1.6.0/" not in readme
    assert "/blob/main/doc/channel/" not in readme
    assert "/blob/main/samples/channel/" not in readme
    assert "/blob/HEAD/doc/channel/quickstart.md" in readme
    assert "/blob/HEAD/doc/channel/reference.md" in readme
    assert "/blob/HEAD/samples/channel/echo_bot.py" in readme
    assert (ROOT / "doc/channel/quickstart.md").is_file()
    assert (ROOT / "doc/channel/reference.md").is_file()
    assert (ROOT / "samples/channel/echo_bot.py").is_file()


def test_channel_docs_do_not_link_to_unreleased_tag():
    docs = [ROOT / "README.md", *sorted((ROOT / "doc/channel").glob("*.md"))]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "/blob/v1.6.0/" not in text, str(path)


def test_markdown_caption_docs_match_current_media_support():
    text = (ROOT / "doc/channel/markdown.md").read_text(encoding="utf-8")

    assert "Images and videos can include an optional markdown caption" in text
    assert "captions are supported for image and video messages only" in text
    assert "file or audio dictionary inputs is rejected" in text
    assert "Images and files can include an optional markdown caption" not in text
    assert "caption` on audio/video dictionary inputs is ignored" not in text


def test_channel_docs_python_fences_parse():
    for path in sorted((ROOT / "doc/channel").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for index, match in enumerate(re.finditer(r"```python\n(.*?)```", text, re.S), 1):
            ast.parse(match.group(1), filename=f"{path} fence {index}")


def test_channel_sample_compiles():
    sample = ROOT / "samples/channel/echo_bot.py"
    compile(sample.read_text(encoding="utf-8"), str(sample), "exec")
