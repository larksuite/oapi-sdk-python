"""Lark User Access Token Device Flow.

Implements the three steps:
    1. start: POST /open-apis/authen/v2/oauth/device_authorization → get
       verification_uri + user_code + device_code + expires_in + interval
    2. wait: the user clicks the URL in Lark, enters the user_code, grants
       scopes
    3. poll: POST /open-apis/authen/v2/oauth/token with grant_type=device_code
       until we get access_token / refresh_token

Refresh uses grant_type=refresh_token on the same /token endpoint.

This client deliberately does NOT import the Lark HTTP transport — we go
straight to `httpx` so it's easy to unit-test with `respx` / mock.
"""

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from lark_oapi.core.const import FEISHU_DOMAIN
from lark_oapi.core.log import logger

from ..errors import UATAuthError
from ..types import UAT

_HTML_TAG_RE = re.compile(r"<[^>]*>")


def _safe_body_snippet(text: str, limit: int = 200) -> str:
    """Strip HTML tags and truncate, so an unexpected upstream response body
    can't flow verbatim into a user-visible card prompt."""
    if not text:
        return ""
    stripped = _HTML_TAG_RE.sub(" ", text)
    collapsed = " ".join(stripped.split())
    if len(collapsed) > limit:
        return collapsed[:limit] + "…"
    return collapsed


@dataclass
class DeviceFlowInit:
    verification_uri: str
    verification_uri_complete: str
    user_code: str
    device_code: str
    expires_in: int
    interval: int = 5


class DeviceFlowClient:
    def __init__(
            self,
            app_id: str,
            app_secret: str,
            *,
            domain: str = FEISHU_DOMAIN,
            timeout: float = 30.0,
            http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._app_id = app_id
        self._app_secret = app_secret
        self._domain = domain.rstrip("/")
        self._timeout = timeout
        self._http = http_client
        # Whether we own the client (and therefore must close it in `close()`).
        # This is locked at construction — if a user-supplied client later
        # appears closed, we fall back to a new internally-owned client (so the
        # SDK stays usable) but we never *downgrade* an internally-owned
        # client's ownership or *claim* ownership of the user's original.
        self._owns_http = http_client is None

    async def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self._timeout)
            self._owns_http = True
        elif getattr(self._http, "is_closed", False):
            # User-supplied client closed out from under us, or our own client
            # was closed by some other path. Either way we must fall back to a
            # fresh internally-owned client; we do NOT touch the user's
            # original object again and we claim ownership of the *new* one.
            self._http = httpx.AsyncClient(timeout=self._timeout)
            self._owns_http = True
        return self._http

    async def close(self) -> None:
        if self._http is not None and self._owns_http:
            try:
                await self._http.aclose()
            except Exception:  # pragma: no cover - defensive
                pass
            self._http = None

    async def start(self, scopes: List[str]) -> DeviceFlowInit:
        body = {
            "client_id": self._app_id,
            "scope": " ".join(scopes) if scopes else "",
        }
        data = await self._post("/open-apis/authen/v2/oauth/device_authorization", body)
        if data.get("code") and data.get("code") != 0:
            raise UATAuthError(f"device_authorization failed: {data.get('msg')}")
        # Some deployments return top-level fields; others wrap in data.
        payload = data.get("data") or data
        return DeviceFlowInit(
            verification_uri=payload.get("verification_uri") or "",
            verification_uri_complete=payload.get("verification_uri_complete")
                                      or payload.get("verification_uri") or "",
            user_code=payload.get("user_code") or "",
            device_code=payload.get("device_code") or "",
            expires_in=int(payload.get("expires_in") or 600),
            interval=int(payload.get("interval") or 5),
        )

    async def poll(
            self,
            device_code: str,
            *,
            interval: int = 5,
            timeout_seconds: Optional[int] = None,
    ) -> UAT:
        """Poll until authorization completes, scopes are denied, or timeout."""
        deadline = time.time() + (timeout_seconds or 600)
        delay = max(1, interval)
        while time.time() < deadline:
            body = {
                "client_id": self._app_id,
                "client_secret": self._app_secret,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
            }
            resp = await self._post("/open-apis/authen/v2/oauth/token", body)
            code = resp.get("code")
            if code == 0 or "access_token" in resp or "access_token" in (resp.get("data") or {}):
                return self._to_uat(resp)
            err = resp.get("error") or resp.get("msg") or ""
            if err in ("authorization_pending", "slow_down"):
                if err == "slow_down":
                    delay += 2
                await asyncio.sleep(delay)
                continue
            if err in ("access_denied", "expired_token"):
                raise UATAuthError(f"device flow failed: {err}")
            # Lark-specific non-zero code
            if isinstance(code, int) and code != 0:
                raise UATAuthError(f"device flow error code={code} msg={resp.get('msg')}")
            await asyncio.sleep(delay)
        raise UATAuthError("device flow timed out")

    async def refresh(self, refresh_token: str) -> UAT:
        body = {
            "client_id": self._app_id,
            "client_secret": self._app_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        resp = await self._post("/open-apis/authen/v2/oauth/token", body)
        code = resp.get("code")
        if isinstance(code, int) and code != 0 and "access_token" not in resp:
            raise UATAuthError(f"refresh failed: {resp.get('msg')}")
        return self._to_uat(resp)

    def _to_uat(self, resp: Dict[str, Any]) -> UAT:
        payload = resp.get("data") if isinstance(resp.get("data"), dict) else resp
        now = time.time()
        expires_in = int(payload.get("expires_in") or 0)
        refresh_expires_in = int(payload.get("refresh_token_expires_in") or 0)
        scope_str = payload.get("scope") or ""
        return UAT(
            access_token=payload.get("access_token") or "",
            refresh_token=payload.get("refresh_token"),
            expires_at=now + expires_in if expires_in else None,
            refresh_expires_at=now + refresh_expires_in if refresh_expires_in else None,
            scopes=scope_str.split() if scope_str else [],
            raw=payload if isinstance(payload, dict) else {},
        )

    async def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = self._domain + path
        client = await self._client()
        r = await client.post(url, json=body)
        content_type = r.headers.get("content-type") or ""
        try:
            data = r.json()
            if isinstance(data, dict):
                return data
        except Exception:  # pragma: no cover
            pass
        # Non-JSON response (HTML error page, WAF block, etc.). Log the full
        # body at WARNING for diagnosis but surface a *truncated + stripped*
        # version upstream so it cannot flow verbatim into user-visible card
        # prompts (`uat_runner` embeds resp["msg"] into a card).
        logger.warning(
            "device flow: unexpected response %s %s body=%r",
            r.status_code, content_type, r.text[:1024],
        )
        return {"code": r.status_code, "msg": _safe_body_snippet(r.text)}


def uat_needs_refresh(uat: UAT, *, slack_seconds: int = 300) -> bool:
    if uat.expires_at is None:
        return False
    return uat.expires_at - time.time() <= slack_seconds
