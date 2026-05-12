# Webhook Server Adapter

The Channel SDK does not ship a built-in HTTP server. TLS termination, rate
limiting, IP allowlisting, anomaly tracking, and framework choice belong in
your application or gateway layer.

Channel exposes one async request entry point:

```python
status, body_bytes = await channel.handle_webhook_request(headers, body)
```

`handle_webhook_request(...)` decrypts the body when `encrypt_key` is
configured, validates `verification_token` when configured, verifies request
signatures for non-challenge events when `encrypt_key` is configured, and routes
the event to your registered `channel.on(...)` handlers. Signature headers may
be present even when event encryption is disabled; without `encrypt_key`, the
dispatcher treats the request as plaintext and does not verify those headers.

You must initialize the channel before the first request. In async frameworks,
prefer `await channel.connect_until_ready()` during application startup. The
synchronous `channel.start()` method is safe in synchronous setup code, but it
may block while initial setup runs.

## aiohttp Adapter

```bash
pip install "lark-oapi[aiohttp]"
```

```python
from aiohttp import web

from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    encrypt_key="...",
    verification_token="...",
    transport="webhook",
)

async def on_message(msg):
    await channel.send(msg.chat_id, {"text": f"echo: {msg.content_text}"})

channel.on("message", on_message)

async def webhook(request: web.Request) -> web.Response:
    status, body_bytes = await channel.handle_webhook_request(
        headers=dict(request.headers),
        body=await request.read(),
    )
    return web.Response(status=status, body=body_bytes, content_type="application/json")

async def init() -> web.Application:
    app = web.Application()
    app.router.add_post("/feishu/webhook", webhook)
    await channel.connect_until_ready()
    return app

if __name__ == "__main__":
    web.run_app(init(), host="127.0.0.1", port=8765)
```

## FastAPI Adapter

```bash
pip install "lark-oapi[fastapi]"
```

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    encrypt_key="...",
    verification_token="...",
    transport="webhook",
)

async def on_message(msg):
    await channel.send(msg.chat_id, {"text": f"echo: {msg.content_text}"})

channel.on("message", on_message)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await channel.connect_until_ready()
    try:
        yield
    finally:
        await channel.disconnect()

app = FastAPI(lifespan=lifespan)

@app.post("/feishu/webhook")
async def webhook(request: Request):
    status, body_bytes = await channel.handle_webhook_request(
        headers=dict(request.headers),
        body=await request.body(),
    )
    return Response(status_code=status, content=body_bytes, media_type="application/json")
```

## Synchronous Setup

If your framework has synchronous startup code and you are in webhook mode,
`channel.start()` builds the dispatcher and returns after initial setup:

```python
channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    transport="webhook",
)
channel.start()
```

Do not call `handle_webhook_request(...)` before startup, or it raises
`FeishuChannelError(code=not_connected)`.

## Rate Limiting and Anomaly Tracking

These belong in your web layer's middleware. For aiohttp:

```python
from collections import defaultdict
from time import time

from aiohttp import web

WINDOW_S = 60
MAX_REQ = 120
_buckets = defaultdict(list)

@web.middleware
async def rate_limit(request, handler):
    ip = request.remote or ""
    now = time()
    bucket = _buckets[ip]
    bucket[:] = [t for t in bucket if t > now - WINDOW_S]
    if len(bucket) >= MAX_REQ:
        return web.Response(status=429, text="rate limited")
    bucket.append(now)
    return await handler(request)

app = web.Application(middlewares=[rate_limit])
```

For anomaly tracking, wrap the handler and track non-200 responses per IP or
tenant key. The SDK only sees validated request bytes and event payloads.

## Why No Built-in Server?

- Avoid forcing aiohttp, FastAPI, or another framework into every SDK user.
- Production deployments usually already have ingress, WAF, and monitoring.
- A framework adapter is small and keeps ownership of HTTP concerns clear.

Return to [Channel module](../channel.md).
