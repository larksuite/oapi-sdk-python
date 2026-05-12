# Markdown to Post Conversion

Channel sends `{"markdown": ...}` and bare string messages as Feishu post
messages. The SDK converts markdown into a post AST before calling the message
API.

If you want a plain text message, send `{"text": "..."}` explicitly.

## Configuration

```python
from lark_oapi.channel import FeishuChannel, MarkdownConverter, OutboundConfig

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    outbound=OutboundConfig(
        markdown_converter=MarkdownConverter(tag_md_mode="native"),
    ),
)
```

## Modes

| Mode | When to use | Rendering behavior |
|---|---|---|
| `structured` (default) | Deterministic rendering across clients, code blocks, links, and SDK-side wire-format assertions | Parses markdown into explicit post nodes such as `tag:text`, `tag:a`, and `tag:code_block`. Feishu post has no native heading, blockquote, or nested-list nodes, so those constructs are flattened or approximated. |
| `native` | Richer user-facing markdown rendering in Feishu clients | Wraps markdown into `tag:md` nodes and lets the Feishu client render it. Headings, quotes, and lists render closer to native markdown, but exact output depends on client version. |

`MarkdownConverter.enabled` exists for compatibility with the config schema. Do
not rely on `enabled=False` to send plain text; use `{"text": ...}` instead.

## Choosing a Mode

- Use `structured` when you need predictable cross-client output or testable
  post ASTs.
- Use `native` when user-facing markdown structure matters more than exact
  cross-client parity.
- Use `{"text": ...}` for plain text.

## Native Mode Notes

- Rendering is delegated to the Feishu client markdown parser.
- `OutboundPost(post=prebuilt_ast)` is passed through and is not affected by
  `tag_md_mode`.
- Structured mentions are inserted as post `tag:at` nodes in the first row.
  They are not written as literal `<at>` text inside a `tag:md` string.

## Wire Format Comparison

Input:

````
# Hello

> world

```python
print("hi")
```
````

`tag_md_mode="structured"`:

```json
{"zh_cn": {"title": "", "content": [
  [{"tag": "text", "text": "Hello", "style": ["bold"]}],
  [{"tag": "text", "text": "│ "}, {"tag": "text", "text": "world"}],
  [{"tag": "code_block", "language": "PYTHON", "text": "print(\"hi\")"}]
]}}
```

`tag_md_mode="native"`:

```json
{"zh_cn": {"title": "", "content": [
  [{"tag": "md", "text": "# Hello\n\n> world"}],
  [{"tag": "md", "text": "```python\nprint(\"hi\")\n```"}]
]}}
```

## Editing Messages

`FeishuChannel.edit_message(message_id, message)` accepts the same high-level
outbound shapes as `send()` for editable text/post messages:

```python
await channel.edit_message(message_id, "# Markdown heading")
await channel.edit_message(message_id, {"markdown": "**bold**"})
await channel.edit_message(message_id, {"text": "plain text"})
await channel.edit_message(message_id, {"post": prebuilt_post_ast})
```

Cards are updated with `update_card(message_id, card)`, not `edit_message()`.
Media, share, and sticker messages are not editable through `edit_message()`.

## Image and Video Captions

Images and videos can include an optional markdown caption:

```python
await channel.send(chat_id, {"image": {"source": image_url}, "caption": "Generated screenshot"})
await channel.send(chat_id, {"video": {"source": video_bytes}, "caption": "Demo clip"})
```

When no caption is provided, image/video messages use the normal `image` or
`media` message type. With a caption, the SDK sends a single post message that
contains the rendered caption followed by an image or video node. Caption
markdown follows `OutboundConfig.markdown_converter`.

In this release, captions are supported for image and video messages only.
`caption` on file or audio dictionary inputs is rejected with `format_error`
before upload. Send the caption as a separate message if two-message semantics
are acceptable.

Return to [Channel module](../channel.md).
