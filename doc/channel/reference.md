# Channel Reference

This is the detailed reference for `FeishuChannel`. For a narrative guide, see
[Channel module](../channel.md). For first-run setup, see [Channel quickstart](./quickstart.md).

## Entry Point

```python
from lark_oapi.channel import FeishuChannel
```

`FeishuChannel` combines WebSocket or webhook event transport, inbound message
normalization, safety policy, deduplication, outbound sending, media
upload/download, streaming replies, and card helpers.

Use lower-level `WSClient`, `EventDispatcherHandler`, or `Client` directly when
your integration only needs raw event dispatch or direct OpenAPI calls.

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

## Constructor Options

| Option | Required | Description |
|---|---:|---|
| `app_id` / `app_secret` | yes | Feishu app credentials |
| `domain` | no | Feishu, Lark, or custom OpenAPI domain |
| `log_level` | no | SDK log level |
| `transport` | no | `"ws"` by default, or `"webhook"` |
| `encrypt_key` | if configured | Webhook/event decryption key from the developer console |
| `verification_token` | if configured | Webhook/event verification token from the developer console |
| `policy` | no | `PolicyConfig` for DM/group admission and mention behavior |
| `safety` | no | `SafetyConfig` for dedup, stale window, batching, and per-chat queue |
| `inbound` | no | `InboundConfig` for normalization, media, names, and reaction behavior |
| `outbound` | no | `OutboundConfig` for chunking, retry, markdown conversion, SSRF, and streaming throttle |
| `uat` | no | `UATConfig` for user access token device-flow behavior |
| `token_store` | no | Custom user access token store |
| `dedup_store` | no | Pipeline-layer `DedupStore` |
| `safety_cache` | no | Safety-layer `ICache` |
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

## Lifecycle

| Method | Purpose |
|---|---|
| `await channel.connect()` | Start transport. In WebSocket mode, keep running until stopped. |
| `await channel.connect_until_ready(timeout=30)` | Start in the background and return after readiness. |
| `await channel.start_background(timeout=30)` | Alias-style background startup with explicit naming. |
| `await channel.disconnect()` | Drain safety batches and stop the transport. |
| `channel.start()` | Synchronous startup. In webhook mode, build the dispatcher and return. |
| `channel.stop()` | Synchronous teardown. |
| `await channel.wait_ready(timeout=30)` | Wait for readiness after startup. |

`start()` is synchronous and may block during initial setup, including bot
identity resolution. Prefer `connect_until_ready()` in async web framework
startup hooks.

## Event Listening

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

Dispatched event names:

| Event | Payload |
|---|---|
| `message` | `InboundMessage` |
| `cardAction` | `CardActionEvent` |
| `reaction` | `ReactionEvent` |
| `botAdded` | `BotAddedEvent` |
| `botLeave` | `BotLeaveEvent` |
| `messageRead` | `MessageReadEvent` |
| `comment` | `CommentEvent` |
| `reject` | `RejectEvent` |
| `reconnecting` | no argument |
| `reconnected` | no argument |
| `error` | exception or `OutboundSendError` |

Snake-case aliases such as `card_action`, `bot_added`, `bot_leave`, and
`message_read` are normalized for compatibility.

## Message Model

`message` handlers receive an `InboundMessage`.

| Field | Description |
|---|---|
| `message_id` / `id` | Feishu message id |
| `create_time` | Original event timestamp |
| `conversation` | `Conversation(chat_id, chat_type, thread_id)` |
| `chat_id` | Shortcut for `conversation.chat_id` |
| `chat_type` | `p2p`, `group`, `topic`, or `unknown` |
| `sender` | `Identity` for the sender |
| `sender_id` | Shortcut for `sender.open_id` |
| `sender_name` | Optional display name |
| `mentions` | List of `Mention` objects |
| `mentioned_all` | Whether the message mentioned all members |
| `mentioned_bot` | Whether the message mentioned the bot |
| `reply_to_message_id` | Parent message id when present |
| `content` | Typed `MessageContent` dataclass |
| `content_text` | Flattened markdown/XML-style text |
| `resources` | Resource descriptors for download |
| `raw_content_type` | Original Feishu message type |
| `raw` | Original event payload |

## Policy

Defaults:

- `dm_policy="open"`
- `group_policy="open"`
- `require_mention=True`
- `respond_to_mention_all=False`
- `sender_identity_fields=["open_id"]`

Runtime update:

```python
channel.update_policy(
    require_mention=False,
    respond_to_mention_all=True,
    group_policy="allowlist",
    group_allowlist=["oc_xxx"],
)
```

`update_policy()` accepts keyword changes for fields on `PolicyConfig`.

## Sending Messages

`channel.send(to, message, opts=None)` accepts:

- a bare string, treated as markdown;
- a dict;
- a typed `Outbound*` dataclass.

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

`opts` may be a `SendOpts` object or a dict:

```python
await channel.send(
    chat_id,
    {"markdown": "please check"},
    {
        "reply_to": message_id,
        "reply_in_thread": True,
        "receive_id_type": "chat_id",
        "reply_target_gone": "fresh",
        "uuid": "optional-idempotency-key",
    },
)
```

For structured mentions, use typed outbound messages:

```python
from lark_oapi.channel import Identity, OutboundText

await channel.send(
    chat_id,
    OutboundText(
        text="please check",
        mentions=[Identity(open_id="ou_xxx", display_name="Alice")],
    ),
)
```

Media `source` accepts:

- HTTP(S) URL string, guarded by `OutboundConfig.ssrf_allowlist`;
- local file path string;
- `bytes`;
- existing media key string for the matching message kind: `img_...` for
  images, `file_...` for file/audio/video. Stickers use
  `{"sticker": {"file_key": ...}}` instead of media `source`.

Image and video messages support `caption`; file and audio captions are rejected
with `format_error`.

## Streaming

Markdown stream:

```python
async def producer(stream):
    for token in ["hello", " ", "world"]:
        await stream.append(token)

await channel.stream(chat_id, {"markdown": producer}, {"reply_to": message_id})
```

Card stream:

```python
async def producer(stream):
    await stream.update(next_card_json)

await channel.stream(
    chat_id,
    {"card": {"initial": initial_card_json, "producer": producer}},
)
```

For low-level CardKit preallocation, see [Streaming with CardKit](./cardkit-streaming.md).

## Helpers

| Method | Return | Notes |
|---|---|---|
| `await channel.update_card(message_id, card)` | `SendResult` | Replace a sent card message |
| `await channel.edit_message(message_id, message)` | `SendResult` | Text/post only |
| `await channel.recall_message(message_id)` | `SendResult` | Recall/delete a message |
| `await channel.add_reaction(message_id, emoji_type)` | `SendResult` | Add a reaction |
| `await channel.remove_reaction(message_id, reaction_id)` | `SendResult` | Remove a reaction by id |
| `await channel.download_resource(file_key, resource_type="image")` | `bytes \| None` | Returns `None` on API failure |
| `await channel.download_resource_to_file(...)` | `Path` | Raises `download_failed` when no body is returned |
| `await channel.get_chat_info(chat_id)` | `ChatInfo \| None` | Returns `None` on API failure |
| `channel.client` | `Client` | Underlying OpenAPI client |

## Error Handling

`send()` returns `SendResult`.

- Invalid input and transport/coercion failures may raise.
- Upstream send failures usually return `SendResult(success=False, error=...)`.
- Both raised errors and failed `SendResult.error` are forwarded to
  `channel.on("error", handler)`.

`stream()` and low-level CardKit helpers raise for controller or CardKit
failures.

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

## Related Documents

- [Channel quickstart](./quickstart.md)
- [Webhook server adapter](./webhook-server.md)
- [Streaming with CardKit](./cardkit-streaming.md)
- [Markdown to post conversion](./markdown.md)
- [Two-layer dedup architecture](./dedup-architecture.md)
