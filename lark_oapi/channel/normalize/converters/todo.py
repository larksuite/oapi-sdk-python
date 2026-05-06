"""Converter: TodoContent → ``<todo>...</todo>`` block.

Aligned with node-sdk's ``converters/todo.ts``: emits title + body + due-time
lines wrapped in ``<todo>``. Falls back to ``<todo>\\n[todo]\\n</todo>`` if
none of the three fields are present.
"""

from typing import List, Tuple

from ...types import ResourceDescriptor, TodoContent
from ._utils import millis_to_datetime


def convert(content: TodoContent) -> Tuple[str, List[ResourceDescriptor]]:
    lines: List[str] = []
    if content.title:
        lines.append(content.title)
    if content.body:
        lines.append(content.body)
    due = millis_to_datetime(content.due_time)
    if due:
        lines.append(f"Due: {due}")
    if not lines:
        return "<todo>\n[todo]\n</todo>", []
    return "<todo>\n" + "\n".join(lines) + "\n</todo>", []
