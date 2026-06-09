"""SSRF guard for outbound media URL fetches.

We block DNS-resolved IPs that fall into well-known private / link-local /
loopback / multicast / reserved CIDR blocks, including IPv6 equivalents and
IPv4-embedding IPv6 forms (``::ffff:``, ``2002::``, ``64:ff9b::``, Teredo).

**Important caveat — TOCTOU / DNS-rebinding.** This guard resolves the
hostname once to validate the IPs, but :mod:`httpx` then performs its own
DNS resolution when it actually connects. An attacker who controls DNS for
the hostname (short TTL) can return a public IP to the guard and a private
IP (e.g. ``169.254.169.254``) to httpx. Fully closing that window requires
pinning the resolved IP into the transport, which is not implemented here.

For that reason, the :mod:`..uploader` caller **requires an explicit
hostname allowlist** when downloading from URLs — this guard is defense in
depth, not a full boundary. If you need URL downloads in a hostile-input
environment, provide an allowlist of trusted content hosts. Otherwise use
``kind='buffer'`` or ``kind='file'`` media sources.
"""

import asyncio
import ipaddress
import socket
from typing import List, Optional
from urllib.parse import urlparse

from ...errors import FeishuChannelErrorCode, FeishuChannelError

# IPv4 CIDR blocklist: private / loopback / link-local / multicast / reserved.
_BLOCKED_V4 = [
    ("0.0.0.0", 8),  # this-network
    ("10.0.0.0", 8),  # private
    ("127.0.0.0", 8),  # loopback
    ("169.254.0.0", 16),  # link-local
    ("172.16.0.0", 12),  # private
    ("192.168.0.0", 16),  # private
    ("100.64.0.0", 10),  # CGNAT
    ("192.0.0.0", 24),  # protocol assignments
    ("192.0.2.0", 24),  # TEST-NET-1
    ("198.18.0.0", 15),  # benchmarking
    ("198.51.100.0", 24),  # TEST-NET-2
    ("203.0.113.0", 24),  # TEST-NET-3
    ("224.0.0.0", 4),  # multicast
    ("240.0.0.0", 4),  # reserved
]


def _ipv4_blocked(ip: str) -> bool:
    try:
        addr = ipaddress.IPv4Address(ip)
    except ValueError:
        return False
    for network, prefix in _BLOCKED_V4:
        try:
            if addr in ipaddress.IPv4Network(f"{network}/{prefix}", strict=False):
                return True
        except ValueError:
            continue
    return False


def _ipv6_blocked(ip: str) -> bool:
    try:
        addr = ipaddress.IPv6Address(ip)
    except ValueError:
        return False
    if addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_unspecified:
        return True
    # Unique local addresses (fc00::/7)
    if addr.packed[0] in (0xfc, 0xfd):
        return True
    # IPv4-mapped (::ffff:a.b.c.d) delegates to IPv4 policy.
    if addr.ipv4_mapped is not None:
        return _ipv4_blocked(str(addr.ipv4_mapped))
    # 6to4 (2002::/16) embeds an IPv4 in bits 16-47 — delegate to IPv4 policy
    # so 2002:a9fe:a9fe:: (encoding 169.254.169.254) is blocked.
    if addr.sixtofour is not None:
        return _ipv4_blocked(str(addr.sixtofour))
    # NAT64 well-known prefix 64:ff9b::/96 embeds an IPv4 in the low 32 bits.
    # ipaddress has no property for this; check prefix manually.
    if addr.packed[:12] == b"\x00\x64\xff\x9b\x00\x00\x00\x00\x00\x00\x00\x00":
        embedded_v4 = ".".join(str(b) for b in addr.packed[12:])
        return _ipv4_blocked(embedded_v4)
    # Teredo (2001::/32) embeds an IPv4 client address in bits 96-127 (inverted).
    if addr.teredo is not None:
        # teredo returns (server_v4, client_v4); the client is the one actually
        # reachable by the packet's destination, so check both.
        server_v4, client_v4 = addr.teredo
        if _ipv4_blocked(str(server_v4)) or _ipv4_blocked(str(client_v4)):
            return True
    return False


async def assert_public_url(
        url: str,
        *,
        allowlist: Optional[List[str]] = None,
) -> None:
    """Raise FeishuChannelError(ssrf_blocked) if `url` resolves to a private IP.

    - Protocol must be http/https.
    - If `hostname` is in `allowlist`, we skip DNS + IP checks.
    - Otherwise we `getaddrinfo` the hostname and verify every resolved
      address is public.
    """
    try:
        u = urlparse(url)
    except ValueError as e:
        raise FeishuChannelError(
            FeishuChannelErrorCode.SSRF_BLOCKED,
            f"invalid url: {e}",
            context={"url": redact_url_for_log(url)},
        ) from e
    safe_url = redact_url_for_log(url)
    if u.scheme not in ("http", "https"):
        raise FeishuChannelError(
            FeishuChannelErrorCode.SSRF_BLOCKED,
            f"protocol {u.scheme!r} not allowed",
            context={"url": safe_url},
        )
    hostname = u.hostname or ""
    if not hostname:
        raise FeishuChannelError(
            FeishuChannelErrorCode.SSRF_BLOCKED,
            "url has no hostname",
            context={"url": safe_url},
        )
    if allowlist and hostname in allowlist:
        return

    # Resolve hostname via getaddrinfo; offload to thread so we don't block.
    loop = asyncio.get_running_loop()
    try:
        infos = await loop.run_in_executor(
            None, lambda: socket.getaddrinfo(hostname, None)
        )
    except socket.gaierror as e:
        raise FeishuChannelError(
            FeishuChannelErrorCode.SSRF_BLOCKED,
            f"dns resolve failed: {e}",
            context={"url": safe_url, "hostname": hostname},
        ) from e

    for family, _type, _proto, _canon, sockaddr in infos:
        ip = sockaddr[0] if isinstance(sockaddr, tuple) else None
        if not ip:
            continue
        if family == socket.AF_INET and _ipv4_blocked(ip):
            raise FeishuChannelError(
                FeishuChannelErrorCode.SSRF_BLOCKED,
                f"blocked ipv4 {ip}",
                context={"url": safe_url, "ip": ip},
            )
        if family == socket.AF_INET6 and _ipv6_blocked(ip):
            raise FeishuChannelError(
                FeishuChannelErrorCode.SSRF_BLOCKED,
                f"blocked ipv6 {ip}",
                context={"url": safe_url, "ip": ip},
            )


def redact_url_for_log(url: str) -> str:
    """Return a URL safe for logs/errors: no credentials, query, or fragment."""
    try:
        u = urlparse(url)
        hostname = u.hostname or ""
        if not hostname:
            return "<invalid-url>"
        netloc = hostname
        if u.port is not None:
            netloc = f"{netloc}:{u.port}"
        return u._replace(netloc=netloc, query="", fragment="").geturl()
    except Exception:
        return "<redacted-url>"
