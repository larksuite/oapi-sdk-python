"""MP4 / ISO BMFF duration parser — zero dependencies.

Walks the box tree looking for `moov/mvhd`, then reads `timescale` + `duration`
from the mvhd payload. Handles:

- Box size encoded as the first 4 bytes (big-endian uint32)
- Extended size (`size == 1`): reads a 64-bit BE size at offset +8, payload
  begins at offset +16
- End-of-file markers (`size == 0` means "extends to EOF")
- Two `mvhd` layout versions:
    - v0 (version byte 0): times are 32-bit, duration at +16
    - v1 (version byte 1): times are 64-bit, duration at +20

Returns `None` on any malformed input.
"""

import struct
from typing import Optional, Tuple


def parse_mp4_duration(buf: bytes) -> Optional[int]:
    """Return duration in milliseconds, or None if unparseable."""
    moov = _find_box(buf, 0, len(buf), b"moov")
    if moov is None:
        return None
    moov_start, moov_end = moov
    mvhd = _find_box(buf, moov_start, moov_end, b"mvhd")
    if mvhd is None:
        return None
    mvhd_start, mvhd_end = mvhd
    if mvhd_end - mvhd_start < 32:
        return None
    version = buf[mvhd_start]
    try:
        if version == 0:
            # creation(4) + modification(4) + timescale(4) + duration(4)
            timescale = struct.unpack_from(">I", buf, mvhd_start + 12)[0]
            duration = struct.unpack_from(">I", buf, mvhd_start + 16)[0]
        else:
            # creation(8) + modification(8) + timescale(4) + duration(8)
            timescale = struct.unpack_from(">I", buf, mvhd_start + 20)[0]
            duration = struct.unpack_from(">Q", buf, mvhd_start + 24)[0]
    except struct.error:
        return None
    if not timescale or duration <= 0:
        return None
    return int(round((duration / timescale) * 1000))


def _find_box(buf: bytes, start: int, end: int, wanted: bytes) -> Optional[Tuple[int, int]]:
    """Scan sibling boxes between [start, end); return (payload_start, payload_end)."""
    i = start
    while i + 8 <= end:
        try:
            size = struct.unpack_from(">I", buf, i)[0]
            box_type = buf[i + 4: i + 8]
        except struct.error:
            return None
        header_len = 8
        if size == 1:
            # Extended size — 64-bit follows
            if i + 16 > end:
                return None
            size = struct.unpack_from(">Q", buf, i + 8)[0]
            header_len = 16
        elif size == 0:
            # Extends to EOF
            size = end - i
        if size < header_len or i + size > end:
            return None
        payload_start = i + header_len
        payload_end = i + size
        if box_type == wanted:
            return payload_start, payload_end
        i += size
    return None
