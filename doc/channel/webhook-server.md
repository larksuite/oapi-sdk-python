# Webhook Server Adapter

The Channel SDK does not ship a built-in HTTP server — rate limiting,
IP allowlisting, anomaly tracking, and TLS termination are deployment
concerns. Instead, the SDK exposes one async method:

```python
status, body_bytes = await channel.handle_webhook_request(headers, body)
```

`handle_webhook_request` does encrypt_key decryption, verification_token
check, and signature verification, then routes the event to your registered
`channel.on(...)` handlers. The return value is `(status_code, body_bytes)`
ready to write to your HTTP response.

## aiohttp adapter (~30 lines)

Install the optional aiohttp dependency:

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
    transport="webhook",  # webhook mode skips WS startup
)

@channel.on("message")
async def on_message(msg):
    await channel.send(msg.conversation.chat_id, {"text": f"echo: {msg.content_text}"})


async def webhook(request: web.Request) -> web.Response:
    body = await request.read()
    status, body_bytes = await channel.handle_webhook_request(
        headers=dict(request.headers),
        body=body,
    )
    return web.Response(status=status, body=body_bytes, content_type="application/json")


async def init() -> web.Application:
    app = web.Application()
    app.router.add_post("/feishu/webhook", webhook)
    channel.start()  # builds the dispatcher; non-blocking in webhook mode
    return app


if __name__ == "__main__":
    web.run_app(init(), host="127.0.0.1", port=8765)
```

## starlette / fastapi

Install the optional FastAPI dependency:

```bash
pip install "lark-oapi[fastapi]"
```

```python
from fastapi import FastAPI, Request, Response
from lark_oapi.channel import FeishuChannel

app = FastAPI()
channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    encrypt_key="...",
    verification_token="...",
    transport="webhook",
)

@app.on_event("startup")
async def _start():
    channel.start()

@app.post("/feishu/webhook")
async def webhook(request: Request):
    body = await request.body()
    status, body_bytes = await channel.handle_webhook_request(
        headers=dict(request.headers),
        body=body,
    )
    return Response(status_code=status, content=body_bytes, media_type="application/json")
```

## Adding rate limiting / anomaly tracking

These belong in your web layer's middleware, not the SDK. For aiohttp:

```python
from aiohttp import web
from collections import defaultdict
from time import time

WINDOW_S = 60
MAX_REQ = 120
_buckets = defaultdict(list)  # remote_ip -> [timestamp, ...]

@web.middleware
async def rate_limit(request, handler):
    ip = request.remote
    now = time()
    bucket = _buckets[ip]
    bucket[:] = [t for t in bucket if t > now - WINDOW_S]
    if len(bucket) >= MAX_REQ:
        return web.Response(status=429, text="rate limited")
    bucket.append(now)
    return await handler(request)

# attach when building the app:
app = web.Application(middlewares=[rate_limit])
```

For anomaly tracking (e.g. running counters of non-200 responses per IP),
wrap the handler — the SDK never sees those concerns.

## Why no built-in server?

The Channel SDK deliberately stays framework-agnostic:

- **Dependency hygiene**: shipping aiohttp / starlette would drag a web
  framework into every consumer of the SDK, including pure-WS users.
- **Production deployments already have an HTTP layer** (sidecar, ingress,
  WAF, gateway) that handles rate-limiting and anomaly tracking. A
  built-in SDK server would be redundant or conflict with deployment
  policy.
- **Adapter is ~30 lines.** The framework choice is yours.
