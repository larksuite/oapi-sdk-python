"""Validation and URL rewriting for handshake-only connection settings."""
from typing import Mapping, Optional
from urllib.parse import urlsplit
from lark_oapi.ws.exception import ClientException


def validate_connection_host(host: Optional[str]) -> None:
    if host is None:
        return
    if not isinstance(host, str) or not host.strip() or "/" in host or "?" in host:
        raise ValueError("invalid websocket connection host")


def snapshot_connection_headers(headers: Optional[Mapping[str, str]]):
    if headers is not None and not isinstance(headers, Mapping):
        raise ValueError("invalid websocket connection headers")
    snapshot = dict(headers) if headers is not None else {}
    for name in snapshot:
        # Pass other names/values to websockets without SDK format checks.
        if (not isinstance(name, str) or name.lower() in ("host", "connection", "upgrade")
                or name.lower().startswith("sec-websocket-")):
            raise ValueError("invalid websocket connection headers")
    return snapshot


def build_connection_url(endpoint: str, host: Optional[str]) -> str:
    if host is None:
        return endpoint
    try:
        parsed = urlsplit(endpoint)
        if (parsed.scheme not in ("ws", "wss") or not parsed.hostname
                or parsed.username is not None or "#" in endpoint):
            raise ValueError()
        # Replace only authority; retain raw path/query and their escaping.
        start = endpoint.index("://") + 3
        return endpoint[:start] + host + endpoint[start + len(parsed.netloc):]
    except (ValueError, TypeError):
        raise ClientException(400, "invalid websocket connection endpoint") from None
