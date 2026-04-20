# Channel Quickstart

`lark_oapi.channel` is the high-level Feishu Channel capability layer. It
wraps WebSocket event subscription, webhook request dispatch, inbound message
normalization, outbound sending, retries, deduplication, and media upload
safety behind `FeishuChannel`.

Use Channel when you are building a conversational bot that needs normalized
message events, replies, media upload/download, markdown rendering, streaming
answers, card interactions, and reconnect handling. If your application only
needs to receive a few raw events and run custom dispatching, the lower-level
`WSClient` and `EventDispatcherHandler` APIs are still available.

## Install

```bash
pip install lark-oapi
```

## WebSocket Echo Bot

Create a bot application in the Feishu developer console, enable event
subscriptions, grant the message scopes required by your bot, and enable the
WebSocket event subscription channel for the app.

Minimum setup for this echo bot:

- Enable message receive events for the bot.
- Grant bot message send / receive scopes such as `im:message` and
  `im:message:send_as_bot`, then re-install the app into the tenant.
- Export the app credentials before running:

```bash
export LARK_APP_ID=cli_xxx
export LARK_APP_SECRET=your_app_secret
python samples/channel/echo_bot.py
```

The sample uses environment variables so credentials do not need to be
committed to source code:

```python
import asyncio
import os
from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(
    app_id=os.environ["LARK_APP_ID"],
    app_secret=os.environ["LARK_APP_SECRET"],
)

@channel.on("message")
async def on_message(msg):
    await channel.send(
        msg.conversation.chat_id,
        {"text": f"echo: {msg.content_text}"},
    )

asyncio.run(channel.connect())
```

For a runnable file, see
[`samples/channel/echo_bot.py`](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/samples/channel/echo_bot.py).

Register `channel.on("error", handler)` for centralized logging of handler,
send, and stream failures. WebSocket reconnects are surfaced through
`"reconnecting"` and `"reconnected"` events.

`channel.connect()` blocks for the WebSocket lifetime. Call
`await channel.disconnect()` during graceful shutdown when your application
owns the event loop.

## Sending and Streaming

`channel.send(to, message, opts=None)` accepts simple dict inputs or the
typed `Outbound*` dataclasses exported from `lark_oapi.channel`:

```python
await channel.send(chat_id, {"text": "plain text"})
await channel.send(chat_id, {"markdown": "hello **world**"})
await channel.send(chat_id, {"card": {"schema": "2.0", "body": {"elements": []}}})
await channel.send(chat_id, {"image": {"source": "./demo.png"}})
await channel.send(chat_id, {"share_chat": {"chat_id": "oc_xxx"}})
```

For token-by-token or LLM-style output, prefer the high-level
`channel.stream(...)` API. It owns the CardKit preallocation flow, throttling,
and finish call:

```python
async def produce(stream):
    for token in ["hello", " ", "world"]:
        await stream.append(token)

await channel.stream(
    chat_id,
    {"markdown": produce},
    {"reply_to": message_id},
)
```

For lower-level CardKit controls, see
[`doc/channel/cardkit-streaming.md`](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/cardkit-streaming.md).

## Webhook Transport

Install an HTTP framework adapter. For the aiohttp example below:

```bash
pip install "lark-oapi[aiohttp]"
```

When you prefer HTTP callbacks, construct the channel with
`transport="webhook"` and pass each HTTP request to
`handle_webhook_request(headers, body)`. The SDK verifies the callback,
normalizes the event, and returns `(status_code, response_body)` for your HTTP
response.

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

@channel.on("message")
async def on_message(msg):
    await channel.send(msg.conversation.chat_id, {"text": f"echo: {msg.content_text}"})

async def webhook(request):
    status, body = await channel.handle_webhook_request(
        headers=dict(request.headers),
        body=await request.read(),
    )
    return web.Response(status=status, body=body, content_type="application/json")

app = web.Application()
app.router.add_post("/feishu/webhook", webhook)
channel.start()
web.run_app(app)
```

The SDK intentionally does not ship an HTTP server. Keep TLS termination,
rate limiting, IP allowlisting, and anomaly tracking in your web framework or
gateway layer. See
[`doc/channel/webhook-server.md`](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/webhook-server.md)
for adapter details.

## Public API Surface

Import Channel APIs from `lark_oapi.channel`:

```python
from lark_oapi.channel import FeishuChannel, OutboundText, SendOpts
```

Do not use `lark_oapi.channel.tests` as application examples. Tests are
internal regression coverage and are excluded from the published package.

For event names, message fields, send inputs, low-level helpers, and common
operational issues, see the
[Channel reference](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/reference.md).
