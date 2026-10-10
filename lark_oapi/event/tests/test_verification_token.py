import json
import pytest
from lark_oapi.core.model import RawRequest
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler

MISSING = object()


def make_payload(schema, token):
    payload = {"schema": "2.0", "header": {"event_type": "audit.test"}, "event": {}}
    target = payload["header"]
    if schema == "v1":
        payload = {"uuid": "audit-id", "type": "event_callback", "event": {"type": "audit.test"}}
        target = payload
    elif schema == "challenge":
        payload = {"type": "url_verification", "challenge": "fixture"}
        target = payload
    if token is not MISSING:
        target["token"] = token
    return json.dumps(payload).encode()


def make_dispatcher(token, hits):
    return (EventDispatcherHandler.builder("", token)
            .register_p1_customized_event("audit.test", lambda data: hits.append(data))
            .register_p2_customized_event("audit.test", lambda data: hits.append(data)).build())


def request(body):
    req = RawRequest()
    req.uri = "/audit"
    req.headers = {}
    req.body = body
    return req


@pytest.mark.parametrize("schema", ["v1", "v2", "challenge"])
@pytest.mark.parametrize("token", ["audit-fixture", "wrong", MISSING, None, "", 123, {}, []])
def test_plaintext_webhook_verifies_every_token(schema, token):
    hits = []
    resp = make_dispatcher("audit-fixture", hits).do(request(make_payload(schema, token)))
    allowed = token == "audit-fixture"
    assert (resp.status_code == 200) == allowed
    assert len(hits) == (1 if allowed and schema != "challenge" else 0)


@pytest.mark.parametrize("configured", [None, ""])
@pytest.mark.parametrize("schema", ["v1", "v2", "challenge"])
@pytest.mark.parametrize("token", [MISSING, None, "", "wrong"])
def test_plaintext_webhook_preserves_missing_configuration(configured, schema, token):
    hits = []
    resp = make_dispatcher(configured, hits).do(request(make_payload(schema, token)))
    allowed = token is MISSING or token is None or token == configured
    assert (resp.status_code == 200) == allowed
    assert len(hits) == (1 if allowed and schema != "challenge" else 0)


def test_trusted_dispatch_does_not_require_webhook_token():
    hits = []
    make_dispatcher("", hits)._do_without_validation(make_payload("v2", MISSING))
    assert len(hits) == 1


def test_v2_does_not_fall_back_to_top_level_token():
    hits = []
    payload = {"schema": "2.0", "token": "audit-fixture", "header": {"event_type": "audit.test"}, "event": {}}
    resp = make_dispatcher("audit-fixture", hits).do(request(json.dumps(payload).encode()))
    assert resp.status_code != 200
    assert hits == []


@pytest.mark.parametrize("valid_signature", [True, False])
def test_encrypted_webhook_preserves_signature_validation(valid_signature):
    import base64
    import hashlib
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad

    hits = []
    key = "encryption-fixture"
    iv = bytes(range(16))
    cipher = AES.new(hashlib.sha256(key.encode()).digest(), AES.MODE_CBC, iv)
    encrypted = base64.b64encode(iv + cipher.encrypt(pad(make_payload("v2", MISSING), 16))).decode()
    req = request(json.dumps({"encrypt": encrypted}).encode())
    signature = hashlib.sha256(b"timestampnonce" + key.encode() + req.body).hexdigest()
    req.headers = {"X-Lark-Request-Timestamp": "timestamp", "X-Lark-Request-Nonce": "nonce", "X-Lark-Signature": signature if valid_signature else "wrong"}
    dispatcher = EventDispatcherHandler.builder(key, None).register_p2_customized_event("audit.test", lambda data: hits.append(data)).build()
    resp = dispatcher.do(req)
    assert (resp.status_code == 200) == valid_signature
    assert len(hits) == (1 if valid_signature else 0)


@pytest.mark.parametrize("token", ["audit-fixture", "wrong", MISSING])
def test_callback_verifies_token_before_handler(token):
    from lark_oapi.event.callback.model.p2_card_action_trigger import P2CardActionTriggerResponse

    hits = []

    def handle_callback(event):
        hits.append(event)
        return P2CardActionTriggerResponse()

    dispatcher = EventDispatcherHandler.builder("", "audit-fixture").register_p2_card_action_trigger(handle_callback).build()
    payload = json.loads(make_payload("v2", token))
    payload["header"]["event_type"] = "card.action.trigger"
    resp = dispatcher.do(request(json.dumps(payload).encode()))
    assert (resp.status_code == 200) == (token == "audit-fixture")
    assert len(hits) == (1 if token == "audit-fixture" else 0)
