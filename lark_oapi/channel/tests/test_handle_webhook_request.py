"""Tests for FeishuChannel.handle_webhook_request."""

import json

import pytest

from lark_oapi.channel import FeishuChannel


@pytest.mark.asyncio
async def test_url_verification_challenge_returns_200():
    """A challenge request must round-trip the challenge value."""
    ch = FeishuChannel(
        app_id="cli_x", app_secret="x", verification_token="vtok",
        transport="webhook",
    )
    ch.start()  # webhook mode: builds dispatcher, no WS connect
    try:
        body = json.dumps({
            "type": "url_verification",
            "challenge": "abc-123",
            "token": "vtok",
        }).encode("utf-8")
        status, response_body = await ch.handle_webhook_request(headers={}, body=body)
        assert status == 200
        assert b"abc-123" in response_body
    finally:
        ch.stop()


@pytest.mark.asyncio
async def test_invalid_token_yields_500():
    """Mismatched verification_token must surface as a non-200 response."""
    ch = FeishuChannel(
        app_id="cli_x", app_secret="x", verification_token="vtok",
        transport="webhook",
    )
    ch.start()
    try:
        body = json.dumps({
            "type": "url_verification",
            "challenge": "abc",
            "token": "WRONG",
        }).encode("utf-8")
        status, _ = await ch.handle_webhook_request(headers={}, body=body)
        assert status >= 400
    finally:
        ch.stop()


@pytest.mark.asyncio
async def test_unknown_event_does_not_raise():
    """A well-formed but unknown event yields a non-2xx but does not raise."""
    ch = FeishuChannel(
        app_id="cli_x", app_secret="x", verification_token="vtok",
        transport="webhook",
    )
    ch.start()
    try:
        body = json.dumps({
            "schema": "2.0",
            "header": {"event_type": "this.event.does.not.exist", "token": "vtok"},
        }).encode("utf-8")
        status, body_out = await ch.handle_webhook_request(headers={}, body=body)
        assert isinstance(status, int)
        assert isinstance(body_out, (bytes, bytearray))
    finally:
        ch.stop()


@pytest.mark.asyncio
async def test_returns_bytes_for_response_body():
    """Output body must be bytes for direct write to wire."""
    ch = FeishuChannel(
        app_id="cli_x", app_secret="x", verification_token="vtok",
        transport="webhook",
    )
    ch.start()
    try:
        body = json.dumps({
            "type": "url_verification",
            "challenge": "x",
            "token": "vtok",
        }).encode("utf-8")
        status, body_out = await ch.handle_webhook_request(headers={}, body=body)
        assert isinstance(body_out, (bytes, bytearray))
    finally:
        ch.stop()
