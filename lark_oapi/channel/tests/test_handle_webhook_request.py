"""Tests for FeishuChannel.handle_webhook_request."""

import json

import pytest

from lark_oapi.card.action_handler import CardActionHandler
from lark_oapi.channel import FeishuChannel
from lark_oapi.core.const import (
    LARK_REQUEST_NONCE,
    LARK_REQUEST_SIGNATURE,
    LARK_REQUEST_TIMESTAMP,
)
from lark_oapi.core.model import RawRequest
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler


def _request(body, headers=None):
    req = RawRequest()
    req.uri = "/callback"
    req.body = json.dumps(body).encode("utf-8")
    req.headers = headers or {}
    return req


def _signature_headers():
    return {
        LARK_REQUEST_SIGNATURE: "signature-from-upstream",
        LARK_REQUEST_TIMESTAMP: "1778579753",
        LARK_REQUEST_NONCE: "nonce",
    }


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


def test_plaintext_event_with_signature_header_does_not_require_encrypt_key():
    seen = []
    handler = (
        EventDispatcherHandler.builder("", "verification-token")
        .register_p2_customized_event("example.event", lambda event: seen.append(event))
        .build()
    )

    resp = handler.do(
        _request(
            {
                "schema": "2.0",
                "header": {
                    "event_type": "example.event",
                    "token": "verification-token",
                },
                "event": {"value": "ok"},
            },
            _signature_headers(),
        )
    )

    assert resp.status_code == 200
    assert resp.content == b'{"msg":"success"}'
    assert len(seen) == 1


def test_event_url_verification_does_not_require_signature_before_dispatch():
    handler = EventDispatcherHandler.builder("encrypt-key", "verification-token").build()

    resp = handler.do(
        _request(
            {
                "type": "url_verification",
                "challenge": "challenge-code",
                "token": "verification-token",
            }
        )
    )

    assert resp.status_code == 200
    assert json.loads(resp.content) == {"challenge": "challenge-code"}


def test_card_callback_with_signature_header_does_not_require_verification_token():
    seen = []
    handler = CardActionHandler.builder("", "").register(lambda card: seen.append(card)).build()

    resp = handler.do(
        _request(
            {
                "type": "card.action.trigger",
                "action": {"value": {"key": "value"}},
            },
            _signature_headers(),
        )
    )

    assert resp.status_code == 200
    assert resp.content == b'{"msg":"success"}'
    assert len(seen) == 1
