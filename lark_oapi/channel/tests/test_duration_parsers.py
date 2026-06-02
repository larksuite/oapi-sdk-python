"""Binary-format duration parsers — synthetic buffers for deterministic tests."""

import struct

from lark_oapi.channel.outbound.media.duration_mp4 import parse_mp4_duration
from lark_oapi.channel.outbound.media.duration_ogg import parse_opus_duration


# ---- OGG / Opus ---------------------------------------------------------


def _ogg_page(granule: int) -> bytes:
    """Build a minimal OggS page header with the given granule position."""
    # Structure: "OggS"(4) + version(1) + type(1) + granule(8) + serial(4)
    # + seq(4) + checksum(4) + n_segs(1) = 27 bytes total
    header = b"OggS"
    header += bytes([0])  # version
    header += bytes([4])  # type = end of stream
    header += struct.pack("<q", granule)  # granule position LE int64
    header += struct.pack("<I", 1)  # serial number
    header += struct.pack("<I", 0)  # page sequence
    header += struct.pack("<I", 0)  # CRC
    header += bytes([0])  # page segments
    return header


def test_opus_duration_reads_final_granule():
    # granule = 48000 → 1000 ms (48 kHz)
    page = _ogg_page(48000)
    assert parse_opus_duration(b"\x00" * 50 + page) == 1000


def test_opus_duration_half_second():
    page = _ogg_page(24000)
    assert parse_opus_duration(page) == 500


def test_opus_duration_uses_last_oggs_page():
    """Multiple pages: parser should read the LAST one's granule."""
    first = _ogg_page(24000)  # would be 500ms
    last = _ogg_page(96000)  # should win: 2000ms
    assert parse_opus_duration(first + b"\x00" * 32 + last) == 2000


def test_opus_duration_none_for_empty_or_short_buffer():
    assert parse_opus_duration(b"") is None
    assert parse_opus_duration(b"tiny") is None


def test_opus_duration_none_without_oggs_magic():
    assert parse_opus_duration(b"A" * 100) is None


def test_opus_duration_negative_granule_rejected():
    # granule -1 as signed int64
    page = _ogg_page(-1)
    assert parse_opus_duration(page) is None


# ---- MP4 / ISO BMFF ------------------------------------------------------


def _box(typ: bytes, payload: bytes) -> bytes:
    size = 8 + len(payload)
    return struct.pack(">I", size) + typ + payload


def _mvhd_v0(timescale: int, duration: int) -> bytes:
    # version(1) + flags(3) + creation(4) + modification(4) + timescale(4)
    # + duration(4) + rate(4) + volume(2) + reserved(10) + matrix(36)
    # + pre_defined(24) + next_track_id(4) = 100 bytes
    payload = bytes([0, 0, 0, 0])  # version + flags
    payload += struct.pack(">I", 0)  # creation
    payload += struct.pack(">I", 0)  # modification
    payload += struct.pack(">I", timescale)
    payload += struct.pack(">I", duration)
    payload += b"\x00" * 76  # rest (padded)
    return _box(b"mvhd", payload)


def _mvhd_v1(timescale: int, duration: int) -> bytes:
    payload = bytes([1, 0, 0, 0])  # version 1 + flags
    payload += struct.pack(">Q", 0)  # creation (64-bit)
    payload += struct.pack(">Q", 0)  # modification (64-bit)
    payload += struct.pack(">I", timescale)
    payload += struct.pack(">Q", duration)  # duration (64-bit)
    payload += b"\x00" * 80  # rest
    return _box(b"mvhd", payload)


def test_mp4_duration_v0_box():
    # timescale=1000 duration=5000 → 5000 ms
    mvhd = _mvhd_v0(1000, 5000)
    moov = _box(b"moov", mvhd)
    # Prepend a skippable ftyp box to simulate a real file
    ftyp = _box(b"ftyp", b"isom\x00\x00\x02\x00")
    assert parse_mp4_duration(ftyp + moov) == 5000


def test_mp4_duration_v1_box():
    mvhd = _mvhd_v1(48000, 24000)  # timescale 48kHz, 24000 ticks = 500 ms
    moov = _box(b"moov", mvhd)
    assert parse_mp4_duration(moov) == 500


def test_mp4_duration_missing_moov_returns_none():
    ftyp = _box(b"ftyp", b"isom\x00\x00\x02\x00")
    assert parse_mp4_duration(ftyp) is None


def test_mp4_duration_missing_mvhd_returns_none():
    moov = _box(b"moov", _box(b"trak", b"\x00" * 32))  # no mvhd inside
    assert parse_mp4_duration(moov) is None


def test_mp4_duration_zero_timescale_returns_none():
    mvhd = _mvhd_v0(0, 5000)
    moov = _box(b"moov", mvhd)
    assert parse_mp4_duration(moov) is None


def test_mp4_duration_extended_size_box():
    """Box with size=1 indicates a 64-bit extended size follows."""
    mvhd = _mvhd_v0(1000, 3000)
    moov_payload = mvhd
    # Construct moov with extended-size header
    extended = b"\x00\x00\x00\x01" + b"moov" + struct.pack(">Q", 16 + len(moov_payload)) + moov_payload
    assert parse_mp4_duration(extended) == 3000


def test_mp4_duration_empty_returns_none():
    assert parse_mp4_duration(b"") is None


def test_mp4_duration_truncated_returns_none():
    assert parse_mp4_duration(b"\x00\x00\x00\x08moov") is None  # header only, no payload
