# Channel Module

[中文](./channel.zh.md)

`lark_oapi.channel` is a high-level module built on top of the OpenAPI
`Client`, WebSocket event transport, and webhook event dispatching. It bundles
event listening, message normalization, safety policy, outbound sending, media
upload/download, card interactions, and streaming replies behind a single
`FeishuChannel` entry point.

Use Channel when you are building a conversational bot that needs normalized
message events, replies, media handling, card callbacks, mention policy, or
transport lifecycle management. If you only need raw event dispatch or direct
OpenAPI calls, use `WSClient`, `EventDispatcherHandler`, or `Client` directly.

## Table of Contents

- [Minimal example](#minimal-example)
- [Constructor options](#constructor-options)
- [Event listening](#event-listening)
- [Lifecycle](#lifecycle)
- [Policy control](#policy-control)
- [Message model](#message-model)
- [Sending messages](#sending-messages)
- [Streaming replies](#streaming-replies)
- [Helpers](#helpers)
- [Error handling](#error-handling)
- [Advanced topics](#advanced-topics)
- [Common issues](#common-issues)

## Minimal Example

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
        {"markdown": f"received: {msg.content_text}"},
        {"reply_to": msg.message_id},
    )

channel.on("message", on_message)

asyncio.run(channel.connect())
```

`connect()` starts the configured transport. In WebSocket mode it opens the
long-lived connection and dispatches events until the process exits or
`disconnect()` is called. In webhook mode, initialize the channel once and pass
HTTP requests to `handle_webhook_request(headers, body)`.

For a runnable file, see [samples/channel/echo_bot.py](../samples/channel/echo_bot.py).

## Constructor Options

`FeishuChannel` accepts flat keyword arguments for common setup and dataclass
configuration for advanced behavior.

| Option | Required | Description |
|---|---:|---|
| `app_id` / `app_secret` | yes | Feishu app credentials |
| `domain` | no | Feishu, Lark, or custom OpenAPI domain |
| `log_level` | no | SDK log level |
| `transport` | no | `"ws"` by default, or `"webhook"` |
| `encrypt_key` | if configured | Webhook/event decryption key from the developer console |
| `verification_token` | if configured | Webhook/event verification token from the developer console |
| `policy` | no | DM/group admission policy and mention behavior |
| `safety` | no | Dedup, stale window, batching, and per-chat queue behavior |
| `inbound` | no | Message normalization, media, name lookup, and reaction behavior |
| `outbound` | no | Chunking, retries, markdown conversion, SSRF allowlist, and streaming throttle |
| `uat` / `token_store` | no | User access token device-flow configuration |
| `dedup_store` / `safety_cache` | no | Pluggable stores for the two dedup layers |
| `name_lookup` | no | Custom `open_id` to display-name resolver |
| `config` | no | Prebuilt `ChannelConfig`; flat kwargs override touched fields |

```python
from lark_oapi.channel import DedupConfig, FeishuChannel, OutboundConfig, RetryConfig, SafetyConfig

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    safety=SafetyConfig(dedup=DedupConfig(ttl_seconds=12 * 3600)),
    outbound=OutboundConfig(retry=RetryConfig(max_attempts=5)),
)
```

## Event Listening

Use string names or constants from `Events`:

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
channel.on(Events.RECONNECTING, on_reconnecting)
channel.on(Events.RECONNECTED, on_reconnected)
channel.on(Events.ERROR, on_error)
```

Dispatched event names are `message`, `cardAction`, `reaction`, `botAdded`,
`botLeave`, `messageRead`, `comment`, `reject`, `reconnecting`,
`reconnected`, and `error`. Snake-case aliases such as `card_action` and
`bot_added` are normalized for compatibility.

`reject` events are emitted when the safety or policy pipeline drops a message.
Known reasons include `stale`, `duplicate`, `lock_contention`, `self_sent`,
`policy_dm_disabled`, `policy_group_disabled`, `policy_dm_not_in_allowlist`,
`policy_group_not_in_allowlist`, `policy_blocklist`, `policy_admin_only`,
`policy_no_mention`, `policy_mention_all_blocked`, and
`policy_sender_not_allowed`.

`error` handlers receive inbound handler exceptions and outbound send/stream
failures forwarded for observability. Direct callers still receive the returned
`SendResult` or raised exception.

## Lifecycle

Use one of these startup patterns:

```python
# Foreground WebSocket process. Blocks until the channel stops.
await channel.connect()

# Async app startup. Returns after transport readiness or timeout.
await channel.connect_until_ready(timeout=30)

# Webhook mode in synchronous setup code. Builds the dispatcher and returns.
channel.start()
```

`start()` is synchronous and performs initial setup, including bot identity
resolution. In async web frameworks, prefer `connect_until_ready()` during
startup so the event loop is not blocked by synchronous setup.

Use `await channel.disconnect()` or `channel.stop()` for shutdown.

## Policy Control

Defaults:

- DM messages are accepted.
- Group messages require an explicit bot mention.
- `@all` does not count as a valid mention unless enabled.
- Self-sent messages are dropped after the bot identity is resolved.

Configure policy at construction time:

```python
from lark_oapi.channel import FeishuChannel, PolicyConfig

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    policy=PolicyConfig(
        group_policy="allowlist",
        group_allowlist=["oc_xxx"],
        require_mention=True,
    ),
)
```

Or update selected fields at runtime:

```python
channel.update_policy(
    require_mention=False,
    respond_to_mention_all=True,
    dm_policy="allowlist",
    allow_from=["ou_xxx"],
)
```

## Message Model

`message` handlers receive an `InboundMessage`. Common fields:

| Field | Description |
|---|---|
| `message_id` / `id` | Feishu message id |
| `chat_id` | Shortcut for `conversation.chat_id` |
| `chat_type` | `p2p`, `group`, `topic`, or `unknown` |
| `sender_id` | Sender `open_id` |
| `sender_name` | Optional display name resolved by the inbound pipeline |
| `content` | Typed content dataclass such as `TextContent`, `ImageContent`, or `FileContent` |
| `content_text` | Flattened markdown/XML-style text for prompts and logs |
| `resources` | Media descriptors for image/file/audio/video/sticker downloads |
| `mentions` | Structured mention objects |
| `mentioned_bot` / `mentioned_all` | Mention policy flags |
| `reply_to_message_id` | Parent message id when the event is a reply |
| `raw_content_type` | Original Feishu message type |
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

Common send options:

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

Do not hand-write `@username` text when you need a real mention. Use
`OutboundText` or `OutboundPost` with `Identity` objects so the SDK emits Feishu
`at` nodes:

```python
from lark_oapi.channel import Identity, OutboundPost

await channel.send(
    chat_id,
    OutboundPost(
        markdown="please check",
        mentions=[Identity(open_id="ou_xxx", display_name="Alice")],
    ),
)
```

Outbound sending has two automatic fallbacks:

- `target_revoked` when replying: resend as a fresh message unless
  `reply_target_gone="fail"` is set.
- `format_error` on post messages: downgrade to plain text when possible.

## Streaming Replies

Use `channel.stream(...)` for token-by-token or long-running output. The
markdown form uses CardKit preallocation internally and handles throttling,
cancellation, and the final `finish_streaming_card(...)` call.

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

For exact CardKit control, use the low-level CardKit methods directly. See
[Streaming with CardKit](./channel/cardkit-streaming.md).

## Helpers

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

`download_resource()` returns `bytes` on success and `None` when the API
download fails. `download_resource_to_file()` raises
`FeishuChannelError(code=download_failed)` when it cannot fetch a body.

## Error Handling

`send()` returns `SendResult`. Transport/coercion failures may raise, while
upstream send failures are returned as `SendResult(success=False, error=...)`.
Both paths are also forwarded to `channel.on("error", handler)`.

`stream()` and low-level CardKit helpers raise exceptions for controller or
CardKit failures.

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

## Advanced Topics

- [Quickstart](./channel/quickstart.md)
- [API reference](./channel/reference.md)
- [Webhook server adapter](./channel/webhook-server.md)
- [Streaming with CardKit](./channel/cardkit-streaming.md)
- [Markdown to post conversion](./channel/markdown.md)
- [Two-layer dedup architecture](./channel/dedup-architecture.md)

## Common Issues

1. Group messages require an `@bot` mention by default. Check event scopes and
   tenant approval before relaxing `PolicyConfig.require_mention`.
2. URL-sourced media requires `OutboundConfig(ssrf_allowlist=[...])`; without
   an allowlist the SDK refuses the download.
3. Card button callbacks require the app to subscribe to card action events and
   the card JSON must emit callback behaviors.
4. Use `channel.stream()` for normal streaming output. Manual CardKit loops must
   keep a strictly increasing `sequence`.
5. Webhook integrations must initialize the channel before calling
   `handle_webhook_request(...)`.
