"""Reuse SDK authentication and request encoding without buffering responses."""

import asyncio
import copy
import threading
import time

import httpx

from lark_oapi.core.http.transport import _build_header, _build_url
from lark_oapi.core.json import JSON
from lark_oapi.core.model import RequestOption
from lark_oapi.core.token import verify

from .options import SSEOptions
from .stream import AsyncSSEStream, SSEStream


def _prepare(config, request, option, options):
    options.validate()
    request = copy.copy(request)
    request.headers = dict(request.headers or {})
    verify(config, request, option)
    headers = httpx.Headers(_build_header(request, option, config))
    headers["Accept"] = "text/event-stream"
    if options.last_event_id:
        if "Last-Event-ID" in headers:
            raise ValueError("conflicting SSE last event ID")
        headers["Last-Event-ID"] = options.last_event_id
    content = (
        JSON.marshal(request.body).encode("utf-8") if request.body is not None else None
    )
    if content is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    return {
        "method": request.http_method.name,
        "url": _build_url(config.domain, request.uri, request.paths),
        "headers": headers,
        "params": request.queries,
        "content": content,
    }


def _validate_response(response):
    response.raise_for_status()
    if (
        response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        != "text/event-stream"
    ):
        raise ValueError("expected text/event-stream response")


def _send_sync(client, raw, options):
    """Bound the complete opening phase; late responses remain worker-owned."""
    condition = threading.Condition()
    state = {"done": False, "abandoned": False, "response": None, "error": None}

    def cancel_open():
        with condition:
            state["abandoned"] = True
            response = state["response"]
            condition.notify_all()
        if response is not None:
            try:
                response.close()
            finally:
                client.close()

    def send():
        response = None
        try:
            response = client.send(raw, stream=True)
        except BaseException as error:  # noqa: BLE001 - propagate worker failures to its caller.
            with condition:
                state["error"] = error
        finally:
            with condition:
                state["done"] = True
                abandoned = state["abandoned"]
                if not abandoned:
                    state["response"] = response
                condition.notify_all()
            if abandoned:
                try:
                    if response is not None:
                        response.close()
                finally:
                    client.close()

    if options.cancellation is not None:
        options.cancellation.bind(cancel_open)
    with condition:
        if state["abandoned"]:
            raise TimeoutError("SSE opening cancelled")
    worker = threading.Thread(target=send, name="lark-sse-open", daemon=True)
    worker.start()  # HTTPX connect/read/pool timeouts bound this worker's lifetime.
    timeout = min(options.open_timeout, options.total_timeout or options.open_timeout)
    with condition:
        ready = condition.wait_for(lambda: state["done"] or state["abandoned"], timeout)
        if not ready or state["abandoned"]:
            state["abandoned"] = True
            raise TimeoutError("SSE opening cancelled or timed out")
        if state["error"] is not None:
            raise state["error"]
        return state["response"]


def open_sse(config, request, option=None, sse_options=None):
    options = sse_options or SSEOptions()
    kwargs = _prepare(config, request, option or RequestOption(), options)
    started = time.monotonic()
    client = httpx.Client(timeout=options.open_timeout, follow_redirects=False)
    response = None
    try:
        raw = client.build_request(**kwargs)
        response = _send_sync(client, raw, options)
        if time.monotonic() - started > options.open_timeout:
            raise TimeoutError("SSE open timed out")
        _validate_response(response)
        raw.extensions["timeout"]["read"] = options.idle_read_timeout
        stream = SSEStream(response, client, options)
        if options.total_timeout is not None:
            remaining = options.total_timeout - (time.monotonic() - started)
            if remaining <= 0:
                stream.close()
                raise TimeoutError("SSE total timeout")
            stream._timer = threading.Timer(remaining, stream._timeout_close)
            stream._timer.daemon = True
            stream._timer.start()
        if options.cancellation is not None:
            options.cancellation.bind(stream.close)
        return stream
    except BaseException:
        if options.cancellation is not None:
            options.cancellation.bind(None)
        try:
            if response is not None:
                response.close()
        finally:
            client.close()
        raise


async def aopen_sse(config, request, option=None, sse_options=None):
    options = sse_options or SSEOptions()
    from functools import partial

    kwargs = await asyncio.get_running_loop().run_in_executor(
        None, partial(_prepare, config, request, option or RequestOption(), options)
    )
    started = time.monotonic()
    client = httpx.AsyncClient(timeout=options.open_timeout, follow_redirects=False)
    response = None
    try:
        raw = client.build_request(**kwargs)
        opening = asyncio.create_task(client.send(raw, stream=True))
        loop = asyncio.get_running_loop()
        if options.cancellation is not None:
            options.cancellation.bind(lambda: loop.call_soon_threadsafe(opening.cancel))
        timeout = min(
            options.open_timeout, options.total_timeout or options.open_timeout
        )
        response = await asyncio.wait_for(opening, timeout)
        _validate_response(response)
        raw.extensions["timeout"]["read"] = options.idle_read_timeout
        stream = AsyncSSEStream(response, client, options)
        loop = asyncio.get_running_loop()
        if options.total_timeout is not None:
            remaining = options.total_timeout - (time.monotonic() - started)
            if remaining <= 0:
                await stream.aclose()
                raise TimeoutError("SSE total timeout")
            stream._deadline = loop.call_later(
                remaining, lambda: stream._schedule_close(timed_out=True)
            )
        if options.cancellation is not None:
            options.cancellation.bind(
                lambda: loop.call_soon_threadsafe(stream._schedule_close)
            )
        return stream
    except BaseException:
        if options.cancellation is not None:
            options.cancellation.bind(None)
        try:
            if response is not None:
                await response.aclose()
        finally:
            await client.aclose()
        raise
