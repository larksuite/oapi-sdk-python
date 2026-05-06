"""CardKit v2 card builder (Python ergonomics helper).

No streaming controller here — streaming is handled by
:mod:`lark_oapi.channel.outbound.streaming` (node-aligned ``update()`` API).
"""

from .builder import CardBuilder, new_card

__all__ = ["CardBuilder", "new_card"]
