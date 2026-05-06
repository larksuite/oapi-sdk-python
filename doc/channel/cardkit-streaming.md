# Streaming with CardKit

CardKit is Feishu's preallocated-card mechanism for typewriter-style streaming
output. For normal LLM-style markdown output, prefer the high-level
`channel.stream(...)` helper:

```python
async def produce(stream):
    for chunk in ["hello", " ", "world"]:
        await stream.append(chunk)

await channel.stream(chat_id, {"markdown": produce}, {"reply_to": message_id})
```

`channel.stream(...)` owns the CardKit preallocation, throttling, cancellation
handling, and final `finish_streaming_card(...)` call. Use the lower-level
methods below only when you need custom CardKit control.

The Channel SDK exposes CardKit preallocation through four coordinated APIs on
`FeishuChannel`:

| Method | Purpose |
|---|---|
| `await channel.create_card_instance(spec)` | Allocate a card_id from a card JSON spec |
| `await channel.send_card_by_reference(to, card_id, ...)` | Send a message that points to the preallocated card |
| `await channel.update_card_element_content(card_id, element_id, content, sequence)` | Patch one element's text — call repeatedly during streaming |
| `await channel.finish_streaming_card(card_id, sequence)` | Close `streaming_mode` so users see the final card |

The high-level `channel.stream(..., {"markdown": producer}, ...)` path wraps
these methods through `MarkdownStreamController` and is the recommended public
API for token streaming.

## Required permissions

A bot must have these scopes enabled in the Feishu developer console **before**
calling any `cardkit/*` API. Without them, calls return a non-zero `code` and
the SDK raises `FeishuChannelError(code=UNKNOWN, message="<raw API response>")`.

| Scope name (zh-CN) | Scope ID | Used by |
|---|---|---|
| 发送消息 | `im:message:send_as_bot` | `send_card_by_reference` |
| 获取与发送单聊、群组消息 | `im:message` | All inbound + outbound message ops |
| 创建卡片实体 | `cardkit:card:write` | `create_card_instance` |
| 更新卡片实体 | `cardkit:card` | `update_card_element_content`, `finish_streaming_card` |

> If your tenant has the legacy `cardkit:card:read`/`cardkit:card:update` split,
> enable both. Newer tenants merge them under `cardkit:card`.

After enabling a scope, the bot must be **re-installed** into the workspace —
existing tokens do not pick up new scopes.

## Sequence semantics

`update_card_element_content(card_id, element_id, content, sequence)` carries
a strictly-increasing `sequence` number per `card_id`. Server contract:

- The first patch must have `sequence >= 1`.
- Each subsequent patch must have `sequence >` the previous one. Reusing or
  going backward can return a non-zero CardKit API code such as `230099`
  (CardKit "failed to create card content"); the SDK surfaces this release's
  CardKit preallocation failures as `FeishuChannelError(UNKNOWN)` with the raw
  API response in the message.
- Gaps are allowed (e.g. 1, 3, 5) — the server does not require contiguity,
  only monotonicity.
- `finish_streaming_card(card_id, sequence)` follows the same rule: its
  `sequence` must exceed the largest sequence used in any
  `update_card_element_content` call for that card.

The recommended pattern: keep a `seq` counter per card, increment **before**
each call, and pass it positionally:

```python
seq = 0
async def patch(text):
    nonlocal seq
    seq += 1
    await channel.update_card_element_content(card_id, "main", text, sequence=seq)

# ... stream tokens, calling patch() ...

seq += 1
await channel.finish_streaming_card(card_id, sequence=seq)
```

## `finish_streaming_card` vs `update_card`

These do **different** things and are not interchangeable:

| Method | When to use | What it does |
|---|---|---|
| `finish_streaming_card(card_id, sequence)` | Streaming output complete | Sets `config.streaming_mode = false` on the preallocated card. Required to remove the typewriter cursor and stop accepting further `update_card_element_content` calls. |
| `update_card(message_id, card)` | One-shot card replacement, no streaming | Replaces the entire card payload of a sent message. Has no `sequence` — uses message_id directly. **Do not** mix with `update_card_element_content`. |

If you need to update a card after `finish_streaming_card` (e.g. attach a
"copy" button after the response is done), use `update_card(message_id, card)`
with the **message_id** of the original send (returned from `send_card_by_reference`),
not the `card_id`.

## API error hints

The SDK raises `FeishuChannelError(UNKNOWN)` for non-zero CardKit responses in
this release. Inspect the raw API response included in the exception message
and use the API code as a troubleshooting hint:

| API code | Likely cause | Fix |
|---|---|---|
| 99991672 / 99991679 | Missing `cardkit:card:write` scope | Add scope, re-install bot |
| 99991680 / 99991681 | Missing `cardkit:card` scope | Add scope, re-install bot |
| 230099 | `sequence` regressed or was reused | Reset stream — allocate a new card_id |
| 230001 | Card JSON spec malformed | Validate against CardKit 2.0 schema |
| 230002 / 230020 | Card already finished, or message recalled | Allocate a new card_id |

## End-to-end example

```python
import asyncio
from lark_oapi.channel import FeishuChannel

async def stream_response(channel, chat_id):
    # 1. Allocate a card_id with streaming_mode on.
    card_id = await channel.create_card_instance({
        "schema": "2.0",
        "config": {"streaming_mode": True, "summary": {"content": ""}},
        "body": {"elements": [{"tag": "markdown", "element_id": "main", "content": "..."}]},
    })

    # 2. Send a placeholder message that references this card.
    result = await channel.send_card_by_reference(chat_id, card_id)
    assert result.success

    # 3. Stream content. Sequence must strictly increase.
    seq = 0
    accumulated = ""
    async for token in produce_tokens():
        accumulated += token
        seq += 1
        await channel.update_card_element_content(
            card_id, "main", accumulated, sequence=seq
        )

    # 4. Close streaming_mode.
    seq += 1
    await channel.finish_streaming_card(card_id, sequence=seq)
```

For the higher-level helper that handles throttling and producer cancellation,
see `lark_oapi/channel/outbound/streaming/markdown_stream.py` and the
`MarkdownStreamController` class.
