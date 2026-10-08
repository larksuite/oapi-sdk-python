import asyncio
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from lark_oapi.core.enum import HttpMethod
from lark_oapi.core.model import BaseRequest, Config
from lark_oapi.core.sse import SSECancellation, SSEOptions, aopen_sse, open_sse
from lark_oapi.core.sse.parser import SSEParser


def test_parser_every_byte_boundary():
    parser = SSEParser(1024, "old")
    text = "\ufeff: hello\r\nid: control\r\n\r\nevent: text.delta\ndata: 中文\ndata: second\nid:\nretry: 1000\n\ndata: incomplete"
    events = []
    for byte in text.encode():
        events.extend(parser.feed(bytes([byte])))
    assert len(events) == 1
    assert events[0].event == "text.delta"
    assert events[0].data == "中文\nsecond"
    assert events[0].id == ""
    assert parser.last_event_id == ""
    assert parser.retry_delay == 1000


def test_parser_limit_without_newline():
    with pytest.raises(ValueError, match="max_event_bytes"):
        list(SSEParser(16).feed(b"data: " + b"x" * 20))


@pytest.fixture
def endpoint():
    release = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"id: first\ndata: first\n\n")
            self.wfile.flush()
            release.wait(5)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    conf = Config()
    conf.domain = f"http://127.0.0.1:{server.server_port}"
    req = BaseRequest()
    req.http_method = HttpMethod.GET
    req.uri = "/events"
    req.token_types = set()
    try:
        yield conf, req
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        worker.join(2)


def test_sync_delivery_and_cancel(endpoint):
    cancel = SSECancellation()
    with open_sse(*endpoint, sse_options=SSEOptions(cancellation=cancel)) as stream:
        assert next(stream).data == "first"
        result = []

        def read():
            try:
                next(stream)
            except (StopIteration, httpx.HTTPError):
                result.append(True)

        worker = threading.Thread(target=read)
        worker.start()
        assert stream.last_event_id == "first"
        cancel.cancel()
        worker.join(1)
        assert not worker.is_alive()
        assert result


def test_sync_idle_timeout(endpoint):
    with open_sse(*endpoint, sse_options=SSEOptions(idle_read_timeout=0.05)) as stream:
        assert next(stream).data == "first"
        with pytest.raises(httpx.ReadTimeout):
            next(stream)


@pytest.mark.asyncio
async def test_async_delivery_and_task_cancel(endpoint):
    async with await aopen_sse(*endpoint) as stream:
        assert (await stream.__anext__()).data == "first"
        task = asyncio.create_task(stream.__anext__())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert stream._closed


def test_sync_open_deadline_and_pre_cancel():
    from unittest.mock import Mock

    from lark_oapi.core.sse.transport import _send_sync

    release = threading.Event()
    closed = threading.Event()
    client = Mock()
    response = Mock()
    response.close.side_effect = closed.set

    def send(*args, **kwargs):
        release.wait(0.2)
        return response

    client.send.side_effect = send
    with pytest.raises(TimeoutError):
        _send_sync(client, Mock(), SSEOptions(open_timeout=0.02))
    release.set()
    assert closed.wait(1)
    response.close.assert_called_once()
    cancel = SSECancellation()
    cancel.cancel()
    cancelled_client = Mock()
    with pytest.raises(TimeoutError):
        _send_sync(cancelled_client, Mock(), SSEOptions(cancellation=cancel))
    cancelled_client.send.assert_not_called()


@pytest.mark.asyncio
async def test_async_external_cancel(endpoint):
    cancel = SSECancellation()
    async with await aopen_sse(
        *endpoint, sse_options=SSEOptions(cancellation=cancel)
    ) as stream:
        assert (await stream.__anext__()).data == "first"
        task = asyncio.create_task(stream.__anext__())
        await asyncio.sleep(0)
        cancel.cancel()
        try:
            await asyncio.wait_for(task, 1)
        except (StopAsyncIteration, httpx.HTTPError):
            pass
        assert stream._closed


def test_close_discards_buffered_events():
    from unittest.mock import Mock

    from lark_oapi.core.sse import SSEStream

    response = httpx.Response(200, content=b"data: first\n\ndata: second\n\n")
    stream = SSEStream(response, Mock(), SSEOptions())
    assert next(stream).data == "first"
    stream.close()
    with pytest.raises(StopIteration):
        next(stream)


def test_sync_total_timeout(endpoint):
    with open_sse(*endpoint, sse_options=SSEOptions(total_timeout=0.3)) as stream:
        assert next(stream).data == "first"
        with pytest.raises(TimeoutError, match="total timeout"):
            next(stream)


@pytest.mark.asyncio
async def test_async_total_timeout(endpoint):
    async with await aopen_sse(
        *endpoint, sse_options=SSEOptions(total_timeout=0.3)
    ) as stream:
        assert (await stream.__anext__()).data == "first"
        with pytest.raises(TimeoutError, match="total timeout"):
            await stream.__anext__()
