"""Converters: Calendar variants → ``<tag>...</tag>`` blocks.

Aligned with node-sdk's ``converters/calendar.ts``. Three variants share the
same inner formatting (📅 summary + 🕙 start ~ end) but use distinct wrapping
tags:

- :class:`CalendarContent`              → ``<calendar_invite>``
- :class:`GeneralCalendarContent`       → ``<calendar>``
- :class:`ShareCalendarEventContent`    → ``<calendar_share>``
"""

from typing import List, Tuple

from ...types import (
    CalendarContent,
    GeneralCalendarContent,
    ResourceDescriptor,
    ShareCalendarEventContent,
)
from ._utils import millis_to_datetime


def _format_inner(summary: str, start_time, end_time) -> str:
    lines: List[str] = []
    if summary:
        lines.append(f"📅 {summary}")
    start = millis_to_datetime(start_time)
    end = millis_to_datetime(end_time)
    if start and end:
        lines.append(f"🕙 {start} ~ {end}")
    elif start:
        lines.append(f"🕙 {start}")
    return "\n".join(lines) if lines else "[calendar event]"


def convert(content: CalendarContent) -> Tuple[str, List[ResourceDescriptor]]:
    inner = _format_inner(content.summary, content.start_time, content.end_time)
    return f"<calendar_invite>\n{inner}\n</calendar_invite>", []


def convert_general(
        content: GeneralCalendarContent,
) -> Tuple[str, List[ResourceDescriptor]]:
    inner = _format_inner(content.summary, content.start_time, content.end_time)
    return f"<calendar>\n{inner}\n</calendar>", []


def convert_share_event(
        content: ShareCalendarEventContent,
) -> Tuple[str, List[ResourceDescriptor]]:
    inner = _format_inner(content.summary, content.start_time, content.end_time)
    return f"<calendar_share>\n{inner}\n</calendar_share>", []
