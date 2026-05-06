# Channel Reference

`FeishuChannel` is the public entry point for the Channel capability layer. It
combines WebSocket or webhook event transport, inbound message normalization,
policy checks, deduplication, outbound sending, media upload/download,
streaming replies, and card helpers.

## When to use Channel

Use Channel for conversational bots: AI chat, streaming replies, interactive
cards, media handling, mention policy, webhook adapters, and long-running
WebSocket connections. Use lower-level `WSClient`, `EventDispatcherHandler`,
or `Client` directly when your integration only needs raw event dispatch or
OpenAPI calls.

## Minimal Example

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
        msg.chat_id,
        {"markdown": f"received: {msg.content_text}"},
        {"reply_to": msg.message_id},
    )

asyncio.run(channel.connect())
```

`connect()` starts the configured transport. In WebSocket mode it opens a
long-lived connection and dispatches events until the process exits or
`disconnect()` is called. In webhook mode, use `start()` once and pass HTTP
requests to `handle_webhook_request(headers, body)`.

## Constructor Options

`FeishuChannel` accepts flat keyword arguments for the common case and
dataclass configuration for advanced behavior:

| Option | Required | Description |
|---|---:|---|
| `app_id` / `app_secret` | yes | Feishu app credentials |
| `encrypt_key` / `verification_token` | webhook | Webhook verification and decryption fields |
| `domain` | no | Feishu/Lark/custom OpenAPI domain |
| `log_level` | no | SDK log level |
| `transport` | no | `"ws"` by default, or `"webhook"` |
| `policy` | no | Group/DM admission policy and mention behavior |
| `safety` | no | Dedup, stale-window, batching, and per-chat queue behavior |
| `inbound` | no | Message normalization and name/media handling |
| `outbound` | no | Chunking, retries, markdown conversion, SSRF allowlist, streaming throttle |
| `uat` / `token_store` | no | User access token device-flow configuration |
| `dedup_store` / `safety_cache` | no | Pluggable stores for dedup and safety state |
| `name_lookup` | no | Custom open_id to display-name resolver |
| `config` | no | Prebuilt `ChannelConfig`; flat kwargs override touched fields |

```python
from lark_oapi.channel import (
    DedupConfig,
    FeishuChannel,
    OutboundConfig,
    RetryConfig,
    SafetyConfig,
)

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    safety=SafetyConfig(dedup=DedupConfig(ttl_seconds=12 * 3600)),
    outbound=OutboundConfig(retry=RetryConfig(max_attempts=5)),
)
```

## Event Listening

Canonical event names are exported through `Events` and type-checked through
`ChannelEventName`:

```python
from lark_oapi.channel import Events

channel.on(Events.MESSAGE, on_message)
channel.on(Events.CARD_ACTION, on_card_action)
channel.on(Events.REACTION, on_reaction)
channel.on(Events.BOT_ADDED, on_bot_added)
channel.on(Events.BOT_LEAVE, on_bot_leave)
channel.on(Events.MESSAGE_READ, on_message_read)
channel.on(Events.COMMENT, on_comment)
channel.on(Events.REJECT, on_reject)
channel.on(Events.RAW, on_raw_event)
channel.on(Events.RECONNECTING, on_reconnecting)
channel.on(Events.RECONNECTED, on_reconnected)
channel.on(Events.ERROR, on_error)
```

`"message"`, `"cardAction"`, `"reaction"`, `"botAdded"`, `"botLeave"`,
`"messageRead"`, `"comment"`, `"reject"`, `"raw"`, `"reconnecting"`,
`"reconnected"`, and `"error"` are accepted. Snake-case aliases such as
`"card_action"` and `"bot_added"` are normalized for compatibility.

## Message Model

`"message"` handlers receive an `InboundMessage`. The fields most handlers
use are:

| Field | Description |
|---|---|
| `message_id` / `id` | Feishu message id |
| `chat_id` | Shortcut for `conversation.chat_id` |
| `chat_type` | `p2p`, `group`, `topic`, or `unknown` |
| `sender_id` | Sender open_id |
| `sender_name` | Optional display name resolved by the inbound pipeline |
| `content` | Typed content dataclass such as `TextContent`, `ImageContent`, or `FileContent` |
| `content_text` | Markdown/XML-style flattened text suitable for prompts and logs |
| `resources` | Media descriptors for image/file/audio/video/sticker downloads |
| `mentions` | Structured mention objects |
| `mentioned_bot` / `mentioned_all` | Mention policy flags |
| `reply_to_message_id` | Parent message id when the event is a reply |
| `raw` | Original event payload |

## Sending Messages

`channel.send(to, message, opts=None)` accepts a bare string, a dict, or an
`Outbound*` dataclass. A bare string is treated as markdown.

```python
await channel.send(chat_id, {"text": "plain text"})
await channel.send(chat_id, {"markdown": "hello **world**"})
await channel.send(chat_id, {"post": {"zh_cn": {"title": "", "content": []}}})
await channel.send(chat_id, {"card": {"schema": "2.0", "body": {"elements": []}}})
await channel.send(chat_id, {"image": {"source": "./image.png"}})
await channel.send(chat_id, {"file": {"source": b"content", "file_name": "a.txt"}})
await channel.send(chat_id, {"audio": {"source": "./audio.ogg"}})
await channel.send(chat_id, {"video": {"source": "./video.mp4"}})
await channel.send(chat_id, {"share_chat": {"chat_id": "oc_xxx"}})
await channel.send(chat_id, {"share_user": {"user_id": "ou_xxx"}})
await channel.send(chat_id, {"sticker": {"file_key": "file_v3_xxx"}})
```

`opts` is either a `SendOpts` object or a dict. Common options:

```python
await channel.send(
    chat_id,
    {"markdown": "please check"},
    {
        "reply_to": message_id,
        "reply_in_thread": True,
        "receive_id_type": "chat_id",
    },
)
```

Do not hand-write `@username` text when you need structured mentions. Use the
typed mention/identity fields supported by the outbound dataclasses so Feishu
placeholders are assembled by the SDK.

## Streaming Replies

Use `channel.stream(...)` for LLM-style output. The markdown form uses
CardKit preallocation internally and handles throttling, cancellation, and
the final `finish_streaming_card` call.

```python
async def write_answer(stream):
    for chunk in ["Thinking", "...", "\nDone"]:
        await stream.append(chunk)

await channel.stream(
    chat_id,
    {"markdown": write_answer},
    {"reply_to": message_id},
)
```

Use the low-level CardKit methods only when you need to own the exact card
allocation and patch sequence:

```python
card_id = await channel.create_card_instance(card_json)
result = await channel.send_card_by_reference(chat_id, card_id)
await channel.update_card_element_content(card_id, "main", "hello", sequence=1)
await channel.finish_streaming_card(card_id, sequence=2)
```

See [CardKit streaming](./cardkit-streaming.md) for sequence rules and
permissions.

## Low-Level Helpers

```python
await channel.update_card(message_id, card_json)
await channel.edit_message(message_id, {"markdown": "updated"})
await channel.recall_message(message_id)
await channel.add_reaction(message_id, "THUMBSUP")
await channel.remove_reaction(message_id, reaction_id)
body = await channel.download_resource(file_key, resource_type="image")
path = await channel.download_resource_to_file(
    file_key,
    resource_type="file",
    dest_dir=download_dir,
)
info = await channel.get_chat_info(chat_id)
raw_client = channel.client
```

## Error Handling

Outbound failures return `SendResult.fail(...)` or raise
`FeishuChannelError`. Register `channel.on("error", handler)` for centralized
observability; direct callers still receive the original return value or
exception.

Known `FeishuChannelErrorCode` values:

| Code | Meaning |
|---|---|
| `format_error` | Message/card schema rejected |
| `target_revoked` | Reply target no longer accepts replies |
| `rate_limited` | Upstream rate limit |
| `permission_denied` | Invalid credentials or missing scopes |
| `upload_failed` | Media upload failed |
| `download_failed` | Media download failed |
| `ssrf_blocked` | URL media download blocked by SSRF policy |
| `send_timeout` | Send/connect timeout |
| `not_connected` | Transport is not connected or startup failed |
| `unknown` | Uncategorized upstream or SDK error |

## Common Issues

- Group messages require an @bot mention by default; tune `PolicyConfig` only
  after checking the app's event scopes and tenant approval.
- URL-sourced media requires `OutboundConfig(ssrf_allowlist=[...])`; without
  an allowlist the SDK refuses the download.
- `file` and `audio` captions are rejected in this release. `image` and
  `video` captions are supported.
- Use `channel.stream()` for normal streaming answers. Manual
  `update_card_element_content(...)` loops must keep a strictly increasing
  CardKit `sequence`.
- Card button callbacks require the app to subscribe to card action events
  and use a card schema that actually emits callbacks.
- Webhook integrations must call `channel.start()` before
  `handle_webhook_request(...)`.
