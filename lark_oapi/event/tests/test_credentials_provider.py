import base64
import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError

import pytest
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from lark_oapi import WebhookCredentials
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.event.callback.model.p2_card_action_trigger import P2CardActionTriggerResponse
from lark_oapi.event.tests.test_verification_token import MISSING, make_payload, request


def make_handler(provider, hits, static_key="", static_token="static-token"):
    builder = EventDispatcherHandler.builder(static_key, static_token)
    builder.webhook_credentials_provider(provider)
    builder.register_p1_customized_event("audit.test", lambda event: hits.append(event))
    builder.register_p2_customized_event("audit.test", lambda event: hits.append(event))

    def callback(event):
        hits.append(event)
        return P2CardActionTriggerResponse()

    return builder.register_p2_card_action_trigger(callback).build()


def encrypted_request(body, key):
    iv = bytes(range(16))
    cipher = AES.new(hashlib.sha256(key.encode()).digest(), AES.MODE_CBC, iv)
    ciphertext = base64.b64encode(iv + cipher.encrypt(pad(body, 16))).decode()
    req = request(json.dumps({"encrypt": ciphertext}).encode())
    signature = hashlib.sha256(b"timestampnonce" + key.encode() + req.body).hexdigest()
    req.headers = {"X-Lark-Request-Timestamp": "timestamp", "X-Lark-Request-Nonce": "nonce", "X-Lark-Signature": signature}
    return req


@pytest.mark.parametrize("schema", ["v1", "v2", "challenge", "callback"])
def test_provider_is_read_once_per_webhook_and_never_at_build(schema):
    calls = []
    hits = []

    def provider():
        calls.append(1)
        return WebhookCredentials(verification_token="dynamic-token")

    handler = make_handler(provider, hits)
    assert calls == []
    body = make_payload("v2" if schema == "callback" else schema, "dynamic-token")
    if schema == "callback":
        payload = json.loads(body)
        payload["header"]["event_type"] = "card.action.trigger"
        body = json.dumps(payload).encode()
    resp = handler.do(request(body))
    assert resp.status_code == 200
    assert len(calls) == 1
    assert len(hits) == (0 if schema == "challenge" else 1)
    assert handler._verification_token == "static-token"


def test_next_request_observes_rotated_credentials():
    hits = []
    state = {"credentials": WebhookCredentials(verification_token="first-token")}
    handler = make_handler(lambda: state["credentials"], hits)
    assert handler.do(request(make_payload("v2", "first-token"))).status_code == 200
    state["credentials"] = WebhookCredentials(verification_token="second-token")
    assert handler.do(request(make_payload("v2", "second-token"))).status_code == 200
    assert handler.do(request(make_payload("v2", "first-token"))).status_code != 200
    assert len(hits) == 2


def test_encrypted_request_uses_one_snapshot_even_during_rotation(monkeypatch):
    hits = []
    calls = []
    state = {"credentials": WebhookCredentials("first-key", "first-token")}

    def provider():
        calls.append(1)
        return state["credentials"]

    handler = make_handler(provider, hits, static_key="static-key")
    decrypt = handler._decrypt

    def rotate_after_decrypt(content, encrypt_key):
        plaintext = decrypt(content, encrypt_key)
        state["credentials"] = WebhookCredentials("second-key", "second-token")
        return plaintext

    monkeypatch.setattr(handler, "_decrypt", rotate_after_decrypt)
    resp = handler.do(encrypted_request(make_payload("v2", "first-token"), "first-key"))
    assert resp.status_code == 200
    assert len(calls) == 1
    assert len(hits) == 1
    assert handler._encrypt_key == "static-key"


@pytest.mark.parametrize("schema", ["v2", "challenge"])
def test_successful_empty_provider_uses_legacy_empty_configuration(schema):
    hits = []
    handler = make_handler(lambda: WebhookCredentials(), hits, static_key="static-key")
    resp = handler.do(request(make_payload(schema, MISSING)))
    assert resp.status_code == 200
    assert len(hits) == (0 if schema == "challenge" else 1)


def test_provider_failure_rejects_without_fallback_or_exception_leaks(caplog):
    hits = []
    secret_marker = "provider-secret-must-not-appear"

    def provider():
        raise RuntimeError(secret_marker)

    resp = make_handler(provider, hits).do(request(make_payload("v2", "static-token")))
    assert resp.status_code != 200
    assert hits == []
    assert secret_marker not in resp.content.decode()
    assert secret_marker not in caplog.text
    assert "webhook credentials provider failed" in resp.content.decode()


@pytest.mark.parametrize("value", [None, {}, 123, ""])
def test_invalid_provider_result_is_not_treated_as_empty_success(value):
    hits = []
    resp = make_handler(lambda: value, hits).do(request(make_payload("v2", "static-token")))
    assert resp.status_code != 200
    assert hits == []


def test_invalid_provider_fields_are_rejected():
    hits = []
    value = WebhookCredentials()
    object.__setattr__(value, "encrypt_key", None)
    resp = make_handler(lambda: value, hits).do(request(make_payload("v2", MISSING)))
    assert resp.status_code != 200
    assert hits == []


def test_trusted_websocket_dispatch_never_reads_provider():
    calls = []
    hits = []

    def provider():
        calls.append(1)
        raise RuntimeError("must not be called")

    make_handler(provider, hits)._do_without_validation(make_payload("v2", MISSING))
    assert calls == []
    assert len(hits) == 1


def test_concurrent_requests_keep_independent_credentials():
    local = threading.local()
    lock = threading.Lock()
    hits = []
    count = []

    def provider():
        with lock:
            count.append(1)
        return WebhookCredentials(verification_token=local.token)

    handler = make_handler(provider, hits)

    def invoke(index):
        local.token = f"request-token-{index}"
        return handler.do(request(make_payload("v2", local.token))).status_code

    with ThreadPoolExecutor(max_workers=4) as executor:
        assert list(executor.map(invoke, range(20))) == [200] * 20
    assert len(hits) == 20
    assert len(count) == 20


def test_credentials_are_immutable_and_do_not_display_values():
    credentials = WebhookCredentials("key-fixture", "token-fixture")
    with pytest.raises(FrozenInstanceError):
        credentials.encrypt_key = "changed"
    assert "key-fixture" not in repr(credentials)
    assert "token-fixture" not in repr(credentials)


def test_provider_registration_validates_callable():
    with pytest.raises(Exception, match="provider must be callable"):
        EventDispatcherHandler.builder("", "").webhook_credentials_provider(123)
