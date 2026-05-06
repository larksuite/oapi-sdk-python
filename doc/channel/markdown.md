# Markdown → Post 转换

Channel SDK 在发送 markdown 消息时，会通过 `MarkdownConverter` 把字符串转成飞书 post 格式。两种渲染模式可选：

| 模式 | 何时使用 | 渲染特点 |
|---|---|---|
| `'structured'`（默认） | 跨客户端确定性渲染、需要结构化节点（语法高亮代码块、可解析链接等） | 解析为 `tag:text`/`tag:a`/`tag:code_block` 等结构化节点。SDK 完全控制渲染。但飞书 post 格式没有 H1/H2/H3 字号节点、没有 blockquote 块级节点、没有嵌套列表节点，这些构造会降级为加粗文本/Unicode 字符前缀/平展列表。 |
| `'native'` | 用户体验依赖飞书原生 markdown 渲染（H1/H2/H3 字号层级、引用块、列表控件） | 把原始 markdown 包成 `tag:md` 节点交由飞书客户端原生 parser 渲染。Code fence 段独立成行（绕过已知客户端边缘行为）。**注意：渲染依赖飞书客户端版本**，不同 PC/移动端可能有差异。 |

## 配置

```python
from lark_oapi.channel.config import OutboundConfig, MarkdownConverter

# 默认（结构化）—— 现有行为，跨客户端一致
config = OutboundConfig()

# 切到 native —— 飞书原生 md 渲染
config = OutboundConfig(
    markdown_converter=MarkdownConverter(tag_md_mode="native"),
)

# 关闭转换 —— 直接发 plain text（enabled=False 优先级高于 tag_md_mode）
config = OutboundConfig(
    markdown_converter=MarkdownConverter(enabled=False),
)
```

## 选型建议

- **跨客户端确定性场景**：选 `'structured'`。例如代码片段需要语法高亮，或需要在 SDK 层断言 wire 格式。
- **AI Agent 回复 / 报告通知 / 富文本通信**：选 `'native'`。AI 输出常用的 H1/H2/H3 章节、bullet 列表、blockquote 在 structured 模式下会丢失视觉层级。
- **不确定时**：先用默认 `'structured'`；遇到具体的渲染回归再切换。

## native 模式注意事项

- 渲染最终由飞书客户端 markdown parser 决定。SDK 不承诺 native 模式跨客户端版本像素一致。
- `OutboundPost(post=<pre_built_ast>)` opaque pass-through 不受 `tag_md_mode` 影响。
- `MarkdownConverter.enabled=False` 优先级高于 `tag_md_mode`：禁用时直接发 plain text，不走 native 路径。
- mentions 仍挂在外层 post 元数据上（与 structured 一致），不内嵌为 `<at>` 字面写进 `tag:md` 节点 text。

## Wire format 对照

输入：

````
# Hello

> world

```python
print('hi')
```
````

`tag_md_mode='structured'`（默认）：

```json
{"zh_cn": {"title": "", "content": [
  [{"tag": "text", "text": "Hello", "style": ["bold"]}],
  [{"tag": "text", "text": "│ "}, {"tag": "text", "text": "world"}],
  [{"tag": "code_block", "language": "PYTHON", "text": "print('hi')"}]
]}}
```

`tag_md_mode='native'`：

```json
{"zh_cn": {"title": "", "content": [
  [{"tag": "md", "text": "# Hello\n\n> world"}],
  [{"tag": "md", "text": "```python\nprint('hi')\n```"}]
]}}
```

## Editing messages

`FeishuChannel.edit_message(message_id, message)` accepts the same high-level
outbound message shapes as `send()` for editable text/post messages:

```python
await channel.edit_message(message_id, "# Markdown heading")
await channel.edit_message(message_id, {"markdown": "**bold**"})
await channel.edit_message(message_id, {"text": "plain text"})
await channel.edit_message(message_id, {"post": prebuilt_post_ast})
```

A bare string is markdown, matching `send(to, "...")`. To edit as plain text,
use `{"text": "..."}` explicitly.

Cards are updated with `update_card(message_id, card)`, not `edit_message()`.
Media/share/sticker messages are not editable through `edit_message()`.

## Image and video captions

Images and videos can include an optional markdown caption:

```python
await channel.send(chat_id, {"image": {"source": image_url}, "caption": "Generated screenshot"})
await channel.send(chat_id, {"video": {"source": video_bytes}, "caption": "Demo clip"})
```

When no caption is provided, image/video messages use the normal `image` or
`media` message type. When a non-empty caption is provided, the SDK sends a
single `post` message containing the rendered caption followed by the image or
video node. Caption markdown follows `OutboundConfig.markdown_converter`,
including `tag_md_mode`.

In this release, captions are supported for image and video messages only.
`caption` on file or audio dictionary inputs is rejected with a format error
before upload. Send the caption as a separate message if two-message semantics
are acceptable.
