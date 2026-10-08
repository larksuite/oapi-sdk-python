"""Connection owners for synchronous and asynchronous pull-based SSE reads."""

import asyncio
import socket
import threading

from .parser import SSEParser


def _interrupt_response(response):
    # HTTPX exposes the network stream as a response extension. Shutdown wakes
    # a blocking read before closing its HTTP resources from another thread.
    stream = response.extensions.get("network_stream")
    sock = stream.get_extra_info("socket") if stream is not None else None
    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass  # Already disconnected: close below still releases ownership.


class SSEStream:
    def __init__(self, response, client, options):
        self.headers = dict(response.headers)
        self._response, self._client = response, client
        self._parser = SSEParser(options.max_event_bytes, options.last_event_id)
        self._closed = False
        self._timed_out = False
        self._close_error = None
        self._lock = threading.Lock()
        self._events = self._iterate()
        self._timer = None
        self._cancellation = options.cancellation

    def __iter__(self):
        return self

    def __next__(self):
        if self._timed_out:
            raise TimeoutError("SSE total timeout")
        if self._close_error is not None:
            raise self._close_error
        if self._closed:
            raise StopIteration
        return next(self._events)

    def _iterate(self):
        try:
            for chunk in self._response.iter_bytes(chunk_size=None):
                if self._closed:
                    return
                yield from self._parser.feed(chunk)
        except Exception as error:
            if self._timed_out:
                raise TimeoutError("SSE total timeout") from error
            raise
        finally:
            self.close()

    @property
    def last_event_id(self):
        return self._parser.last_event_id

    @property
    def retry_delay(self):
        return self._parser.retry_delay

    def close(self):
        with self._lock:
            if self._closed:
                return
            self._closed = True
        if self._timer is not None:
            self._timer.cancel()
        if self._cancellation is not None:
            self._cancellation.bind(None)
        _interrupt_response(self._response)
        try:
            self._response.close()
        finally:
            self._client.close()

    def _timeout_close(self):
        self._timed_out = True
        try:
            self.close()
        except Exception as error:  # noqa: BLE001 - deliver timer cleanup failures to the reader.
            self._close_error = error

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AsyncSSEStream:
    def __init__(self, response, client, options):
        self.headers = dict(response.headers)
        self._response, self._client = response, client
        self._parser = SSEParser(options.max_event_bytes, options.last_event_id)
        self._closed = False
        self._timed_out = False
        self._close_error = None
        self._events = self._iterate()
        self._deadline = None
        self._close_task = None
        self._close_lock = asyncio.Lock()
        self._cancellation = options.cancellation

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._timed_out:
            raise TimeoutError("SSE total timeout")
        if self._close_error is not None:
            raise self._close_error
        if self._closed:
            raise StopAsyncIteration
        return await self._events.__anext__()

    async def _iterate(self):
        try:
            async for chunk in self._response.aiter_bytes():
                if self._closed:
                    return
                for event in self._parser.feed(chunk):
                    yield event
        except Exception as error:
            if self._timed_out:
                raise TimeoutError("SSE total timeout") from error
            raise
        finally:
            await self.aclose()

    @property
    def last_event_id(self):
        return self._parser.last_event_id

    @property
    def retry_delay(self):
        return self._parser.retry_delay

    async def aclose(self):
        async with self._close_lock:
            await self._close_resources()

    async def _close_resources(self):
        if self._closed:
            return
        self._closed = True
        if self._deadline is not None:
            self._deadline.cancel()
        if self._cancellation is not None:
            self._cancellation.bind(None)
        try:
            await self._response.aclose()
        finally:
            await self._client.aclose()

    def _schedule_close(self, timed_out=False):
        self._timed_out = self._timed_out or timed_out
        if self._close_task is None:
            self._close_task = asyncio.create_task(self.aclose())
            self._close_task.add_done_callback(self._observe_close)

    def _observe_close(self, task):
        if not task.cancelled():
            self._close_error = task.exception()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()
