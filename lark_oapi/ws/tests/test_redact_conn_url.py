from lark_oapi.ws.client import _redact_conn_url

FAKE_URL = (
    "wss://msg-frontier.example.test/ws/v2"
    "?fpid=493&access_key=access-key-test-value"
    "&service_id=33554678&ticket=ticket-test-value"
)


def test_redacts_access_key_and_ticket_values():
    redacted = _redact_conn_url(FAKE_URL)
    assert "access-key-test-value" not in redacted
    assert "ticket-test-value" not in redacted
    # Values are masked (urlencode may encode '*' as %2A).
    assert "access_key=" in redacted and "ticket=" in redacted
    assert "*" not in redacted.replace("%2A", "")
    # Non-sensitive parts are preserved (host, path, other query params).
    assert redacted.startswith("wss://msg-frontier.example.test/ws/v2?")
    assert "fpid=493" in redacted
    assert "service_id=33554678" in redacted


def test_keeps_url_without_query():
    url = "wss://msg-frontier.example.test/ws/v2"
    assert _redact_conn_url(url) == url


def test_handles_none():
    assert _redact_conn_url(None) is None
    assert _redact_conn_url("") == ""
