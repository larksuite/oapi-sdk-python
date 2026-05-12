# Channel Quickstart

This guide gets a minimal Channel echo bot running. For the full API surface,
see [Channel module](../channel.md) and [Channel reference](./reference.md).

## Install

```bash
pip install lark-oapi
```

## Prepare the Bot

In the Feishu developer console:

- Create a bot application.
- Enable event subscriptions.
- Enable the WebSocket event subscription channel for local development.
- Subscribe to message receive events.
- Grant bot message send/receive scopes such as `im:message` and
  `im:message:send_as_bot`.
- Re-install the app into the tenant after changing scopes.

Export credentials before running:

```bash
export LARK_APP_ID=cli_xxx
export LARK_APP_SECRET=your_app_secret
```

## Run the Echo Bot

```bash
python samples/channel/echo_bot.py
```

The sample is intentionally small:

```python
import asyncio
import os

from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id=os.environ["LARK_APP_ID"],
    app_secret=os.environ["LARK_APP_SECRET"],
)

async def on_message(msg):
    await channel.send(
        msg.chat_id,
        {"text": f"echo: {msg.content_text}"},
    )

channel.on("message", on_message)

asyncio.run(channel.connect())
```

`connect()` starts the WebSocket transport and keeps the process running. Use
`await channel.disconnect()` during graceful shutdown if your application owns
the event loop.

Register an error handler when you want centralized observability:

```python
async def on_error(err):
    print("channel error:", err)

channel.on("error", on_error)
```

## Send a Reply

```python
await channel.send(
    msg.chat_id,
    {"markdown": f"received: {msg.content_text}"},
    {"reply_to": msg.message_id},
)
```

`channel.send(to, message, opts=None)` accepts dict inputs, typed `Outbound*`
dataclasses, or a bare markdown string.

## Stream a Reply

```python
async def produce(stream):
    for token in ["hello", " ", "world"]:
        await stream.append(token)

await channel.stream(
    msg.chat_id,
    {"markdown": produce},
    {"reply_to": msg.message_id},
)
```

For lower-level CardKit controls, see [Streaming with CardKit](./cardkit-streaming.md).

## Webhook Transport

For HTTP callbacks, construct the channel with `transport="webhook"` and pass
each HTTP request to `handle_webhook_request(headers, body)`.

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

async def webhook(request):
    status, body = await channel.handle_webhook_request(
        headers=dict(request.headers),
        body=await request.read(),
    )
    return web.Response(status=status, body=body, content_type="application/json")

async def init():
    app = web.Application()
    app.router.add_post("/feishu/webhook", webhook)
    await channel.connect_until_ready()
    return app

web.run_app(init())
```

The SDK does not ship a built-in HTTP server. Keep TLS termination, rate
limiting, IP allowlisting, and anomaly tracking in your web framework or
gateway layer. See [Webhook server adapter](./webhook-server.md).

## Next Steps

- [Channel module](../channel.md)
- [Channel reference](./reference.md)
- [Markdown to post conversion](./markdown.md)
- [Two-layer dedup architecture](./dedup-architecture.md)
