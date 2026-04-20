"""Code-fence-aware Markdown splitter tests."""

from lark_oapi.channel.outbound.markdown.splitter import split_with_code_fences


def test_short_passthrough():
    assert split_with_code_fences("hello", limit=100) == ["hello"]


def test_fence_preserved_across_split():
    md = "\n".join([
        "Intro text",
        "```python",
        "print(1)",
        "print(2)",
        "print(3)",
        "print(4)",
        "print(5)",
        "```",
        "Done",
    ])
    chunks = split_with_code_fences(md, limit=40)
    assert len(chunks) >= 2
    for c in chunks:
        # Every chunk that starts with code should properly close
        fences = c.count("```")
        assert fences % 2 == 0, f"unbalanced fences in chunk: {c!r}"


def test_heading_starts_chunk_when_buffer_75_full():
    md = "\n".join(["a" * 85, "# Heading", "body text"])
    chunks = split_with_code_fences(md, limit=100)
    # Heading should land at the start of a later chunk, not end of an earlier one
    heading_first = [i for i, c in enumerate(chunks) if c.startswith("# Heading")]
    assert heading_first, chunks


def test_hard_overflow_single_line():
    very_long = "x" * 250
    chunks = split_with_code_fences(very_long, limit=100)
    # Single-line cannot be split, but splitter should still complete (chunk may exceed limit)
    assert "".join(chunks) == very_long
