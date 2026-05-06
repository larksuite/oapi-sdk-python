"""Converter: HongbaoContent → ``<hongbao .../>``."""

from typing import List, Tuple

from ...types import HongbaoContent, ResourceDescriptor
from ._utils import attr


def convert(content: HongbaoContent) -> Tuple[str, List[ResourceDescriptor]]:
    return f'<hongbao text="{attr(content.text)}"/>', []
