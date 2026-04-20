"""SSRF guard tests — pure local asserts, no network hits."""

import socket
from unittest.mock import patch

import pytest

from lark_oapi.channel.errors import FeishuChannelErrorCode, FeishuChannelError
from lark_oapi.channel.outbound.media.ssrf_guard import assert_public_url, _ipv4_blocked, _ipv6_blocked


def test_private_ipv4_cidrs_blocked():
    for ip in ("10.0.0.1", "127.0.0.1", "169.254.169.254", "172.16.5.1", "192.168.1.1", "100.64.1.1"):
        assert _ipv4_blocked(ip) is True, ip


def test_public_ipv4_allowed():
    for ip in ("1.1.1.1", "8.8.8.8", "93.184.216.34"):
        assert _ipv4_blocked(ip) is False, ip


def test_ipv6_loopback_and_ula_blocked():
    assert _ipv6_blocked("::1") is True
    assert _ipv6_blocked("fe80::1") is True
    assert _ipv6_blocked("fd00::1") is True  # ULA
    assert _ipv6_blocked("fc00::1") is True


def test_ipv6_public_allowed():
    assert _ipv6_blocked("2606:4700:4700::1111") is False


@pytest.mark.asyncio
async def test_non_http_protocol_rejected():
    with pytest.raises(FeishuChannelError) as ei:
        await assert_public_url("file:///etc/passwd")
    assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED


@pytest.mark.asyncio
async def test_private_hostname_rejected():
    with patch("socket.getaddrinfo", return_value=[
        (socket.AF_INET, 0, 0, "", ("10.0.0.5", 0)),
    ]):
        with pytest.raises(FeishuChannelError) as ei:
            await assert_public_url("https://internal.example")
        assert ei.value.code == FeishuChannelErrorCode.SSRF_BLOCKED
        assert "10.0.0.5" in str(ei.value)


@pytest.mark.asyncio
async def test_public_hostname_allowed():
    with patch("socket.getaddrinfo", return_value=[
        (socket.AF_INET, 0, 0, "", ("93.184.216.34", 0)),
    ]):
        await assert_public_url("https://example.com")  # no raise


@pytest.mark.asyncio
async def test_allowlist_bypasses_dns_check():
    # Allowlist entry means we don't even call getaddrinfo
    with patch("socket.getaddrinfo", side_effect=AssertionError("should not be called")):
        await assert_public_url("https://internal.test", allowlist=["internal.test"])
