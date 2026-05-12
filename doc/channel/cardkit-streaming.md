# Streaming with CardKit

For normal markdown streaming, prefer the high-level `channel.stream(...)`
helper:

```python
async def produce(stream):
    for chunk in ["hello", " ", "world"]:
        await stream.append(chunk)

await channel.stream(chat_id, {"markdown": produce}, {"reply_to": message_id})
```

`channel.stream(...)` owns CardKit preallocation, throttling, cancellation
handling, and the final `finish_streaming_card(...)` call. Use the lower-level
methods below only when you need custom CardKit control.

## Low-level APIs

| Method | Purpose |
|---|---|
| `await channel.create_card_instance(spec)` | Allocate a `card_id` from a card JSON spec |
| `await channel.send_card_by_reference(to, card_id, ...)` | Send a message that points to the preallocated card |
| `await channel.update_card_element_content(card_id, element_id, content, sequence)` | Patch one element's text during streaming |
| `await channel.finish_streaming_card(card_id, sequence)` | Close `streaming_mode` so users see the final card |

The high-level `channel.stream(..., {"markdown": producer}, ...)` path wraps
these methods through `MarkdownStreamController` and is the recommended public
API for token streaming.

## Required Permissions

A bot must have the required message and CardKit scopes enabled before calling
CardKit APIs. Scope names can vary by tenant UI; verify the exact names in the
Feishu developer console.

| Scope name (zh-CN) | Scope ID | Used by |
|---|---|---|
| 发送消息 | `im:message:send_as_bot` | `send_card_by_reference` |
| 获取与发送单聊、群组消息 | `im:message` | Inbound and outbound message operations |
| 创建卡片实体 | `cardkit:card:write` | `create_card_instance` |
| 更新卡片实体 | `cardkit:card` | `update_card_element_content`, `finish_streaming_card` |

If your tenant still exposes the legacy `cardkit:card:read` /
`cardkit:card:update` split, enable both. After changing scopes, re-install the
bot into the tenant; existing tokens do not pick up new scopes.

## Sequence Semantics

`update_card_element_content(card_id, element_id, content, sequence)` carries a
strictly increasing `sequence` number per `card_id`.

- The first patch must have `sequence >= 1`.
- Each subsequent patch must have `sequence >` the previous one.
- Gaps are allowed, for example `1, 3, 5`.
- `finish_streaming_card(card_id, sequence)` follows the same rule: its
  `sequence` must exceed the largest sequence used in any update call for that
  card.

Recommended pattern:

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

These methods are not interchangeable.

| Method | When to use | What it does |
|---|---|---|
| `finish_streaming_card(card_id, sequence)` | Streaming output complete | Sets `config.streaming_mode = false` on the preallocated card. |
| `update_card(message_id, card)` | One-shot card replacement | Replaces the whole card payload of a sent message. Uses `message_id`, not `card_id`, and has no `sequence`. |

If you need to update a card after `finish_streaming_card`, use
`update_card(message_id, card)` with the `message_id` returned from
`send_card_by_reference(...)`, not the `card_id`.

## API Error Hints

Low-level CardKit methods raise `FeishuChannelError(code=unknown, ...)` for
non-zero CardKit responses in this release. Inspect the raw API response inside
the exception message and use the upstream API code as a troubleshooting hint.

| API code | Likely cause | Fix |
|---|---|---|
| `99991672` / `99991679` | Missing create-card scope | Add scope and re-install bot |
| `99991680` / `99991681` | Missing update-card scope | Add scope and re-install bot |
| `230099` | `sequence` regressed or was reused | Reset the stream and allocate a new `card_id` |
| `230001` | Card JSON spec malformed | Validate against CardKit 2.0 schema |
| `230002` / `230020` | Card already finished, or message recalled | Allocate a new `card_id` |

## Core Flow Example

This snippet focuses on the CardKit calls. It assumes `channel` is already
connected and `chat_id` is known.

```python
card_id = await channel.create_card_instance({
    "schema": "2.0",
    "config": {"streaming_mode": True, "summary": {"content": ""}},
    "body": {
        "elements": [
            {"tag": "markdown", "element_id": "main", "content": "..."},
        ],
    },
})

send_result = await channel.send_card_by_reference(chat_id, card_id)
if not send_result.success:
    raise RuntimeError(send_result.error)

seq = 0
accumulated = ""
for token in ["hello", " ", "world"]:
    accumulated += token
    seq += 1
    await channel.update_card_element_content(
        card_id,
        "main",
        accumulated,
        sequence=seq,
    )

seq += 1
await channel.finish_streaming_card(card_id, sequence=seq)
```

Return to [Channel module](../channel.md).
