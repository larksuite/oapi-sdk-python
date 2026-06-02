"""Opus-in-OGG duration parser — zero dependencies.

Algorithm:

1. Scan backward from end-of-buffer for the last `OggS` magic (4-byte `b"OggS"`)
2. Read `granule_position` as little-endian int64 at offset +6
3. Convert to milliseconds: Opus is always 48 kHz, so `ms = granule / 48`

Returns `None` on any failure — malformed OGG, not-Opus, negative granule.
"""

import struct
from typing import Optional

OGG_MAGIC = b"OggS"
OPUS_SAMPLES_PER_MS = 48  # Opus mandates a 48 kHz output rate


def parse_opus_duration(buf: bytes) -> Optional[int]:
    """Return duration in milliseconds, or None if unparseable."""
    if not buf or len(buf) < 27:
        return None
    # Scan backward for the last OggS page
    i = len(buf) - 27
    while i >= 0:
        if buf[i: i + 4] == OGG_MAGIC:
            try:
                granule = struct.unpack_from("<q", buf, i + 6)[0]
            except struct.error:
                return None
            if granule < 0:
                return None
            return int(round(granule / OPUS_SAMPLES_PER_MS))
        i -= 1
    return None
