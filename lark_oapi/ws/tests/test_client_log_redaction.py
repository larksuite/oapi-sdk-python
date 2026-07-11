import logging

import pytest

from lark_oapi.ws import client as ws_client


class _FakeConn:
    async def close(self):
        pass


def test_redaction_does_not_treat_fragment_text_as_query():
    url = "wss://example.test/callback#section?access_key=visible"

    assert ws_client._redact_conn_url_for_log(url) == url


@pytest.mark.asyncio
async def test_connection_lifecycle_logs_redact_only_sensitive_query_values(monkeypatch, caplog):
    conn_url = (
        "wss://example.test/callback?device_id=device%20one&service_id=42"
        "&access_key=fake%20access%2Fpart&TICKET=Fake%2fticket&ticket&flag&empty="
        "&ticket=second-fake&access_key=&access_key_extra=visible#section%20one"
    )
    redacted_url = (
        "wss://example.test/callback?device_id=device%20one&service_id=42"
        "&access_key=***&TICKET=***&ticket&flag&empty="
        "&ticket=***&access_key=***&access_key_extra=visible#section%20one"
    )
    connected_urls = []

    async def fake_connect(uri):
        connected_urls.append(uri)
        return _FakeConn()

    client = ws_client.Client("fake_app_id", "fake_app_secret")
    monkeypatch.setattr(client, "_get_conn_url", lambda: conn_url)
    monkeypatch.setattr(ws_client.websockets, "connect", fake_connect)
    monkeypatch.setattr(
        ws_client.loop,
        "create_task",
        lambda coro: coro.close() if hasattr(coro, "close") else None,
    )

    with caplog.at_level(logging.INFO, logger="Lark"):
        await client._connect()
        await client._disconnect()

    lifecycle_messages = [
        record.getMessage()
        for record in caplog.records
        if "connected to " in record.getMessage() or "disconnected to " in record.getMessage()
    ]

    assert connected_urls == [conn_url]
    assert lifecycle_messages == [
        "connected to {} [conn_id=device one]".format(redacted_url),
        "disconnected to {} [conn_id=device one]".format(redacted_url),
    ]
