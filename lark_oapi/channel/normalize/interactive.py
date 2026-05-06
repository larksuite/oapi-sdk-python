"""Interactive (card) message re-fetch + v1/v2 normalization.

The event payload for `msg_type=interactive` is truncated. If the caller opts
in (default), we re-fetch the full card JSON with `GET /im/v1/messages/:id`
and detect the CardKit version.
"""

import inspect
import json
from typing import Any, Dict, Optional

from lark_oapi.core.log import logger

from ..types import InteractiveContent


def _detect_version(card: Dict[str, Any]) -> str:
    if not isinstance(card, dict):
        return "unknown"
    if "schema" in card or "body" in card:
        return "v2"
    if "elements" in card or "config" in card or "i18n_elements" in card:
        return "v1"
    if "card" in card:
        return _detect_version(card.get("card") or {})
    return "unknown"


def _extract_card_json(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Pull the card JSON from a GET /messages/:id response.

    The response wraps the message in `data.items[0].body.content`, which is
    itself a JSON string for interactive messages.
    """
    if not isinstance(payload, dict):
        return None
    data = payload.get("data") or payload
    items = data.get("items") if isinstance(data, dict) else None
    if not items and isinstance(data, dict):
        return _parse_body_content(data.get("body") or {})
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    return _parse_body_content(first.get("body") or {})


def _parse_body_content(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None
    content = body.get("content")
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None
        except ValueError:
            return None
    return None


async def fetch_interactive(message_id: str, fetch_message) -> Optional[InteractiveContent]:
    """Fetch full interactive card JSON for `message_id`.

    `fetch_message(id) -> dict | awaitable[dict]` is injected so this module
    stays testable without a real Lark client.
    """
    try:
        result = fetch_message(message_id)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:  # pragma: no cover - network/defensive
        logger.warning("interactive fetch failed for %s: %s", message_id, e)
        return None
    card = _extract_card_json(result or {})
    if card is None:
        return None
    return InteractiveContent(card=card, card_version=_detect_version(card), raw=card)
