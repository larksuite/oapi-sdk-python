"""Shared request construction; sync and async execution stay in their examples."""

import argparse
import io
import json
import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

import lark_oapi as lark
import lark_oapi.api.agent.v1 as agent
from lark_oapi.core.sse import SSEOptions


def required(name):
    value = os.getenv(name, "")
    if not value or any(c in value for c in "\r\n\0"):
        raise RuntimeError("set a valid " + name + " environment variable")
    return value


def configuration():
    base = os.getenv("OPEN_BASE_URL", "https://open.feishu.cn")
    parsed = urlparse(base)
    local = parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost")
    invalid_endpoint = (
        not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    )
    if invalid_endpoint or not (parsed.scheme == "https" or local):
        raise RuntimeError("OPEN_BASE_URL must be HTTPS (HTTP allowed only for localhost testing)")
    client = (
        lark.Client.builder()
        .app_id(required("APP_ID"))
        .app_secret(required("APP_SECRET"))
        .domain(base)
        .timeout(10)
        .enable_set_token(True)
        .log_level(lark.LogLevel.ERROR)
        .build()
    )
    option = (
        lark.RequestOption.builder()
        .user_access_token(required("USER_ACCESS_TOKEN"))
        .build()
    )
    return client.agent.v1, option


def arguments():
    parser = argparse.ArgumentParser(description="Agent v1 examples; see README.md")
    parser.add_argument("mode", choices=("chat", "upload", "resume", "close", "interrupt"))
    return parser.parse_args()


def checked(response, action):
    if not response.success():
        message = "%s: HTTP %s, code %s" % (
            action,
            response.raw.status_code,
            response.code,
        )
        raise RuntimeError(message)
    if response.data is None:
        raise RuntimeError(action + ": missing response data")
    return response.data


def create_session_request():
    body = (
        agent.CreateSessionRequestBody.builder()
        .uuid(str(uuid.uuid4()))
        .name("SDK Agent example")
        .build()
    )
    return (
        agent.CreateSessionRequest.builder()
        .request_body(body)
        .build()
    )


def message_request(sid):
    # Lightweight union: type is supplied by the caller, never inferred by SDK.
    text = (
        agent.TextItem.builder()
        .type("text")
        .text("请用三句话介绍 SSE。")
        .build()
    )
    contents = [text]
    if os.getenv("AGENT_FILE_URI"):
        contents.append({"type": "file", "uri": required("AGENT_FILE_URI")})
    event = (
        agent.Event.builder()
        .type("user.message")
        .contents(contents)
        .build()
    )
    return event_request(sid, event)


def event_request(sid, event):
    body = (
        agent.CreateSessionEventRequestBody.builder()
        .uuid(str(uuid.uuid4()))
        .events([event])
        .build()
    )
    return (
        agent.CreateSessionEventRequest.builder()
        .session_id(sid)
        .request_body(body)
        .build()
    )


def query_id(data):
    if not data.messages or not data.messages[0].id:
        raise RuntimeError("send message: missing user query id")
    return data.messages[0].id


def stream_request(sid, query):
    return (
        agent.StreamSessionEventRequest.builder()
        .session_id(sid)
        .message_id(query)
        .build()
    )


def stream_options(cursor=""):
    return SSEOptions(
        open_timeout=10,
        idle_read_timeout=60,
        total_timeout=180,
        max_event_bytes=1024 * 1024,
        last_event_id=cursor,
    )


def handle_event(event):
    # data is a JSON string, not a decoded Agent object.
    payload = json.loads(event.data)
    if event.event == "message.failed":
        raise RuntimeError("Agent reply failed")
    if not isinstance(payload, dict):
        raise RuntimeError("SSE data must be a JSON object")
    base = payload.get("BaseResp", {})
    if isinstance(base, dict) and base.get("StatusCode", 0):
        raise RuntimeError("SSE business error: code %s" % base["StatusCode"])
    if event.event in ("text", "text.delta"):
        text = payload.get("text" if event.event == "text" else "delta", "")
        # Deliver text to your UI here. Complete items replace previews by item id.
        print("text received: %d characters" % len(text))
    else:
        print("SSE event=" + json.dumps(event.event))
    message = payload.get("message", {})
    is_assistant = isinstance(message, dict) and message.get("role") == "assistant"
    if is_assistant and message.get("id"):
        print("AGENT_ASSISTANT_MESSAGE_ID=" + str(message["id"]))
    # Persist the exact cursor only AFTER successfully processing the event.
    if event.id is not None:
        print("AGENT_LAST_EVENT_ID=" + json.dumps(event.id))


@contextmanager
def upload_source():
    path = os.getenv("AGENT_FILE_PATH")
    if path:
        if ".." in Path(path).parts:
            raise RuntimeError("AGENT_FILE_PATH must not contain parent traversal")
        stream = Path(path).open("rb")
    else:
        stream = io.BytesIO(b"SDK Agent upload example\n")
    with stream:
        style = os.getenv("AGENT_UPLOAD_STYLE", "io")
        if style not in ("io", "tuple"):
            raise RuntimeError("AGENT_UPLOAD_STYLE must be io or tuple")
        # The explicit body filename overrides this tuple name; MIME is retained.
        value = ("original.tmp", stream, "text/plain") if style == "tuple" else stream
        filename = os.getenv("AGENT_FILENAME", "report.txt")
        body = (
            agent.CreateFileRequestBody.builder()
            .file(value)
            .filename(filename)
            .uuid(str(uuid.uuid4()))
            .build()
        )
        request = (
            agent.CreateFileRequest.builder()
            .request_body(body)
            .build()
        )
        yield request


def uploaded(data):
    if not data.uri:
        raise RuntimeError("upload: missing URI")
    print("AGENT_FILE_URI=" + data.uri)
    print("upload succeeded; set AGENT_FILE_URI and run chat to reference it")


def interrupt_requests():
    sid = required("AGENT_SESSION_ID")
    assistant = required("AGENT_ASSISTANT_MESSAGE_ID")
    event = (
        agent.Event.builder()
        .type("user.interrupt")
        .message_id(assistant)
        .build()
    )
    get = (
        agent.GetSessionMessageRequest.builder()
        .session_id(sid)
        .message_id(assistant)
        .build()
    )
    return event_request(sid, event), get


def reply_status(data):
    if data.message is None:
        raise RuntimeError("query reply: missing message")
    print("reply status=" + json.dumps(data.message.status))
    print(
        "in_progress is an immediate snapshot; "
        "completed may mean it finished before the interrupt"
    )
