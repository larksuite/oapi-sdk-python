"""Smart concat for streaming text deltas.

Different streaming producers yield text in different ways:
- **Delta**: each chunk is a new suffix (`"Hello"` → `" world"`).
- **Accumulated**: each chunk is the running total
  (`"Hello"` → `"Hello world"`).
- **Mixed** — some frameworks switch styles mid-stream.

`merge_streaming_text(prev, next)` handles all three:

    if next startswith prev:   # accumulated; use next
        return next
    if prev startswith next:   # producer rewound; keep prev
        return prev
    # else: compute the largest suffix of prev that is also a prefix of next,
    # drop that prefix from next, and concatenate.
"""


def merge_streaming_text(prev: str, chunk: str) -> str:
    if not chunk:
        return prev
    if not prev:
        return chunk
    if chunk.startswith(prev):
        return chunk
    if prev.startswith(chunk):
        return prev

    # Find the longest suffix of prev that is a prefix of chunk.
    max_overlap = min(len(prev), len(chunk))
    for size in range(max_overlap, 0, -1):
        if prev[-size:] == chunk[:size]:
            return prev + chunk[size:]
    return prev + chunk
