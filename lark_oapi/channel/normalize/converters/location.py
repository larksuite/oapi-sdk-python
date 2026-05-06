"""Converter: LocationContent → ``<location .../>``."""

from typing import List, Tuple

from ...types import LocationContent, ResourceDescriptor
from ._utils import attr


def convert(content: LocationContent) -> Tuple[str, List[ResourceDescriptor]]:
    text = (
        f'<location name="{attr(content.name)}" '
        f'lng="{content.longitude or ""}" lat="{content.latitude or ""}"/>'
    )
    return text, []
