"""Bot identity auto-fetch.

Resolution flow:
    1. Try `GET /open-apis/bot/v3/info` (returns app_id / activate_status / name / open_id).
    2. Fall back to `GET /open-apis/application/v6/applications/:app_id` (richer data).
    3. Return `BotIdentity(open_id, user_id?, name?)`; the caller persists it on
       the channel so group `@Bot` detection works correctly.

The SDK does not ship a `bot.v3` generated resource, so we go through the raw
Transport / BaseRequest primitives with a tenant token.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from lark_oapi.core.const import UTF_8
from lark_oapi.core.enum import AccessTokenType, HttpMethod
from lark_oapi.core.http import Transport
from lark_oapi.core.log import logger
from lark_oapi.core.model import BaseRequest, Config, RawResponse, RequestOption
from lark_oapi.core.token.auth import verify as _verify_auth


@dataclass
class BotIdentity:
    """Resolved bot identity: ``open_id`` plus optional ``user_id`` / ``name``.

    ``name`` defaults to empty string because the ``/bot/v3/info`` fallback
    path may not surface it in some tenant configurations — at which point
    we'd rather degrade than crash. ``app_id`` is included for convenience
    when callers need to correlate identities with their app registration.
    """

    open_id: str
    user_id: Optional[str] = None
    name: str = ""
    app_id: Optional[str] = None


def _raw_request(uri: str, method: HttpMethod = HttpMethod.GET) -> BaseRequest:
    req = BaseRequest()
    req.http_method = method
    req.uri = uri
    req.token_types = {AccessTokenType.TENANT}
    return req


async def fetch_bot_identity(config: Config) -> Optional[BotIdentity]:
    """Return the bot's identity tuple, or None on failure.

    Preferred path: /bot/v3/info — cheap and always available when the bot
    capability is enabled. Falls back to application info.
    """
    primary = await _try_bot_v3_info(config)
    if primary is not None:
        return primary
    return await _try_application_get(config)


async def _try_bot_v3_info(config: Config) -> Optional[BotIdentity]:
    try:
        req = _raw_request("/open-apis/bot/v3/info")
        option = RequestOption()
        # Raw `Transport.aexecute` bypasses the Chain that normally injects
        # the tenant token via `core.token.auth.verify`. Call it explicitly
        # so `option.tenant_access_token` is populated before the request
        # goes out (otherwise the header becomes literal `Bearer None` and
        # Feishu rejects with 400).
        _verify_auth(config, req, option)
        resp = await Transport.aexecute(config, req, option)
        data = _parse_data(resp)
        if not data:
            return None
        bot = data.get("bot") or data
        open_id = bot.get("open_id") or bot.get("openid") or ""
        if not open_id:
            return None
        return BotIdentity(
            open_id=open_id,
            user_id=bot.get("user_id"),
            name=bot.get("app_name") or bot.get("name"),
            app_id=bot.get("app_id") or config.app_id,
        )
    except Exception as e:
        logger.debug("fetch_bot_identity: /bot/v3/info failed: %s", e)
        return None


async def _try_application_get(config: Config) -> Optional[BotIdentity]:
    if not config.app_id:
        return None
    try:
        uri = f"/open-apis/application/v6/applications/{config.app_id}?lang=zh_cn"
        req = _raw_request(uri)
        option = RequestOption()
        _verify_auth(config, req, option)  # inject tenant token; see _try_bot_v3_info
        resp = await Transport.aexecute(config, req, option)
        data = _parse_data(resp)
        if not data:
            return None
        app = data.get("app") or data.get("application") or data
        # application.v6 doesn't directly return open_id; some tenants expose
        # `bot_info.open_id` though. Best-effort extraction.
        open_id = ""
        bot_info = app.get("bot_info") or app.get("bot") or {}
        if isinstance(bot_info, dict):
            open_id = bot_info.get("open_id") or bot_info.get("openid") or ""
        if not open_id:
            return None
        return BotIdentity(
            open_id=open_id,
            name=app.get("app_name") or app.get("name"),
            app_id=config.app_id,
        )
    except Exception as e:
        logger.debug("fetch_bot_identity: /applications fallback failed: %s", e)
        return None


def _parse_data(resp: RawResponse) -> Optional[Dict[str, Any]]:
    if resp is None or resp.content is None:
        return None
    try:
        body = json.loads(resp.content.decode(UTF_8))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(body, dict):
        return None
    if body.get("code") and body.get("code") != 0:
        logger.debug("fetch_bot_identity: api returned code=%s msg=%s", body.get("code"), body.get("msg"))
        return None
    # Most Feishu OpenAPI endpoints wrap payload in a `data` envelope, but
    # `/bot/v3/info` puts `bot` directly at the top level (alongside the
    # `code` / `msg` envelope keys). Support both shapes:
    #   {"data": {"bot": {...}}, "code": 0}  → return data
    #   {"bot": {...}, "code": 0, "msg": ""} → return body minus envelope
    data = body.get("data")
    if isinstance(data, dict):
        return data
    return {k: v for k, v in body.items() if k not in ("code", "msg")}
