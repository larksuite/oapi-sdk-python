"""Shared helpers used across per-type converters."""

import datetime
from typing import Any


def attr(s: Any) -> str:
    """Escape a string for use inside an XML-like attribute value."""
    return (s or "").replace('"', "'").replace("\n", " ")


def format_duration(ms: Any) -> str:
    """Format a millisecond duration as ``12s`` / ``1.5s``."""
    try:
        if not ms:
            return "0s"
        s = ms / 1000.0
        formatted = f"{s:.1f}"
        if "." in formatted:
            return formatted.rstrip("0").rstrip(".") + "s"
        return f"{int(s)}s"
    except Exception:  # pragma: no cover
        return "0s"


def rfc3339_beijing(create_time_ms: Any) -> str:
    """Format a timestamp as ``YYYY-MM-DDTHH:MM:SS+08:00`` (best-effort)."""
    if not create_time_ms:
        return ""
    try:
        ts = int(create_time_ms)
        if ts > 10 ** 12:
            ts = ts / 1000.0
        dt = datetime.datetime.fromtimestamp(
            ts, tz=datetime.timezone(datetime.timedelta(hours=8))
        )
        return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    except Exception:  # pragma: no cover
        return ""


def millis_to_datetime(value: Any) -> str:
    """Format a ms-or-s epoch timestamp as ``YYYY-MM-DD HH:MM:SS``.

    Mirrors node-sdk's ``millisToDatetime`` helper used by calendar / video_chat
    / todo converters. Accepts str-or-int input; returns empty string on any
    parse failure so converters can conditionally omit a line.
    """
    if value in (None, "", 0, "0"):
        return ""
    try:
        ts = int(value)
        if ts > 10 ** 12:
            ts = ts / 1000.0
        dt = datetime.datetime.fromtimestamp(
            ts, tz=datetime.timezone(datetime.timedelta(hours=8))
        )
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:  # pragma: no cover
        return ""
