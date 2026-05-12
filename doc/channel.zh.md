# Channel 模块

[English](./channel.md)

`lark_oapi.channel` 是基于 OpenAPI `Client`、WebSocket 事件传输和 webhook 事件分发封装的高层模块。它把事件监听、消息归一化、安全策略、出站发送、媒体上传下载、卡片交互、流式回复等能力收敛到 `FeishuChannel` 一个入口。

当你要开发会话式机器人，需要处理归一化消息、回复消息、媒体、卡片回调、@ 策略、WebSocket 长连接或 webhook 回调生命周期时，优先使用 Channel。如果只是做原始事件分发或直接调用 OpenAPI，可以继续使用 `WSClient`、`EventDispatcherHandler` 或 `Client`。

## 目录

- [最小示例](#最小示例)
- [初始化参数](#初始化参数)
- [事件监听](#事件监听)
- [生命周期](#生命周期)
- [策略控制](#策略控制)
- [消息模型](#消息模型)
- [发送消息](#发送消息)
- [流式回复](#流式回复)
- [辅助能力](#辅助能力)
- [错误处理](#错误处理)
- [高级主题](#高级主题)
- [常见问题](#常见问题)

## 最小示例

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

`connect()` 会启动配置的传输方式。WebSocket 模式下，它会建立长连接并持续分发事件，直到进程退出或调用 `disconnect()`。webhook 模式下，先初始化 Channel，再把 HTTP 请求交给 `handle_webhook_request(headers, body)`。

可运行示例见 [samples/channel/echo_bot.py](../samples/channel/echo_bot.py)。

## 初始化参数

`FeishuChannel` 支持常用场景的扁平参数，也支持传入 dataclass 配置高级行为。

| 参数 | 是否必填 | 说明 |
|---|---:|---|
| `app_id` / `app_secret` | 是 | 飞书应用凭据 |
| `domain` | 否 | 飞书、Lark 或自定义 OpenAPI 域名 |
| `log_level` | 否 | SDK 日志级别 |
| `transport` | 否 | 默认 `"ws"`，也可设为 `"webhook"` |
| `encrypt_key` | 按后台配置 | 开发者后台配置的事件加密密钥 |
| `verification_token` | 按后台配置 | 开发者后台配置的事件校验 token |
| `policy` | 否 | 单聊/群聊准入策略和 @ 行为 |
| `safety` | 否 | 去重、过期窗口、批处理和单聊串行队列 |
| `inbound` | 否 | 消息归一化、媒体、名称解析和 reaction 行为 |
| `outbound` | 否 | 分片、重试、markdown 转换、SSRF 白名单和流式节流 |
| `uat` / `token_store` | 否 | 用户访问凭证 device-flow 配置 |
| `dedup_store` / `safety_cache` | 否 | 两层去重使用的可插拔存储 |
| `name_lookup` | 否 | 自定义 `open_id` 到展示名的解析器 |
| `config` | 否 | 预构造的 `ChannelConfig`；扁平参数会覆盖对应字段 |

```python
from lark_oapi.channel import DedupConfig, FeishuChannel, OutboundConfig, RetryConfig, SafetyConfig

channel = FeishuChannel(
    app_id="cli_xxx",
    app_secret="***",
    safety=SafetyConfig(dedup=DedupConfig(ttl_seconds=12 * 3600)),
    outbound=OutboundConfig(retry=RetryConfig(max_attempts=5)),
)
```

## 事件监听

可以直接使用字符串事件名，也可以使用 `Events` 常量：

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

实际会分发的事件名包括 `message`、`cardAction`、`reaction`、`botAdded`、`botLeave`、`messageRead`、`comment`、`reject`、`reconnecting`、`reconnected`、`error`。兼容别名如 `card_action`、`bot_added` 会被归一化。

当安全或策略管道丢弃消息时，会触发 `reject`。常见原因包括 `stale`、`duplicate`、`lock_contention`、`self_sent`、`policy_dm_disabled`、`policy_group_disabled`、`policy_dm_not_in_allowlist`、`policy_group_not_in_allowlist`、`policy_blocklist`、`policy_admin_only`、`policy_no_mention`、`policy_mention_all_blocked`、`policy_sender_not_allowed`。

`error` 处理器会收到入站 handler 异常，以及为了观测而转发的出站发送/流式错误。直接调用方仍然会收到原始的 `SendResult` 或异常。

## 生命周期

常用启动方式：

```python
# 前台 WebSocket 进程。会持续运行直到 Channel 停止。
await channel.connect()

# 异步应用启动。等待传输就绪或超时后返回。
await channel.connect_until_ready(timeout=30)

# webhook 模式的同步初始化。构建 dispatcher 后返回。
channel.start()
```

`start()` 是同步方法，会执行初始准备，包括 bot identity 解析。异步 Web 框架里建议在启动阶段使用 `connect_until_ready()`，避免同步初始化阻塞事件循环。

关闭时使用 `await channel.disconnect()` 或 `channel.stop()`。

## 策略控制

默认行为：

- 接收单聊消息。
- 群聊消息默认要求显式 @bot。
- 默认不把 `@all` 当作有效 @。
- bot 身份解析成功后，会丢弃自己发送的消息。

构造时配置策略：

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

运行时更新部分字段：

```python
channel.update_policy(
    require_mention=False,
    respond_to_mention_all=True,
    dm_policy="allowlist",
    allow_from=["ou_xxx"],
)
```

## 消息模型

`message` handler 收到的是 `InboundMessage`。常用字段：

| 字段 | 说明 |
|---|---|
| `message_id` / `id` | 飞书消息 ID |
| `chat_id` | `conversation.chat_id` 的快捷属性 |
| `chat_type` | `p2p`、`group`、`topic` 或 `unknown` |
| `sender_id` | 发送者 `open_id` |
| `sender_name` | 入站管道解析出的可选展示名 |
| `content` | 类型化内容 dataclass，例如 `TextContent`、`ImageContent`、`FileContent` |
| `content_text` | 适合日志和文本处理的 markdown/XML-style 扁平文本 |
| `resources` | 图片、文件、音频、视频、表情等资源描述 |
| `mentions` | 结构化 @ 列表 |
| `mentioned_bot` / `mentioned_all` | @ 策略相关标记 |
| `reply_to_message_id` | 当前消息是回复时的父消息 ID |
| `raw_content_type` | 原始飞书消息类型 |
| `raw` | 原始事件体 |

## 发送消息

`channel.send(to, message, opts=None)` 支持裸字符串、dict 或 `Outbound*` dataclass。裸字符串会被当作 markdown。

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

常用发送选项：

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

需要真正 @ 用户时，不要在文本里手写 `@用户名`。请使用带 `Identity` 的 `OutboundText` 或 `OutboundPost`，由 SDK 生成飞书 `at` 节点：

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

出站发送内置两类自动降级：

- 回复目标已撤回或删除：默认去掉回复关系，改发普通消息；设置 `reply_target_gone="fail"` 可关闭该降级。
- post 结构被拒绝：可解析出纯文本时降级为 text 消息。

## 流式回复

对逐 token 或长耗时输出，使用 `channel.stream(...)`。markdown 流内部使用 CardKit 预创建卡片，负责节流、取消处理和最终 `finish_streaming_card(...)`。

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

如果需要完全控制 CardKit 分配和 patch 序列，可以直接使用底层 CardKit 方法。详见 [Streaming with CardKit](./channel/cardkit-streaming.md)。

## 辅助能力

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

`download_resource()` 成功时返回 `bytes`，下载失败时返回 `None`。`download_resource_to_file()` 在无法获取内容时会抛出 `FeishuChannelError(code=download_failed)`。

## 错误处理

`send()` 返回 `SendResult`。传输或入参转换失败可能直接抛异常，上游发送失败通常返回 `SendResult(success=False, error=...)`。两类错误都会转发给 `channel.on("error", handler)` 方便统一观测。

`stream()` 和底层 CardKit 方法在控制器或 CardKit 调用失败时会抛异常。

稳定错误码：

| Code | 含义 |
|---|---|
| `format_error` | 消息或卡片结构被拒绝 |
| `target_revoked` | 回复目标已无法回复 |
| `rate_limited` | 上游限流 |
| `permission_denied` | 凭据无效或权限不足 |
| `upload_failed` | 媒体上传失败 |
| `download_failed` | 媒体下载失败 |
| `ssrf_blocked` | URL 媒体下载被 SSRF 策略拦截 |
| `send_timeout` | 发送或连接超时 |
| `not_connected` | 传输未连接或启动失败 |
| `unknown` | 未归类的上游或 SDK 错误 |

## 高级主题

- [快速开始（英文）](./channel/quickstart.md)
- [API 参考（英文）](./channel/reference.md)
- [Webhook Server Adapter（英文）](./channel/webhook-server.md)
- [Streaming with CardKit（英文）](./channel/cardkit-streaming.md)
- [Markdown to post conversion（英文）](./channel/markdown.md)
- [Two-layer dedup architecture（英文）](./channel/dedup-architecture.md)

## 常见问题

1. 群聊消息默认需要 @bot。放宽 `PolicyConfig.require_mention` 前，先确认事件权限和租户安装审批。
2. URL 媒体源需要配置 `OutboundConfig(ssrf_allowlist=[...])`；没有白名单时 SDK 会拒绝下载。
3. 卡片按钮回调需要应用订阅卡片 action 事件，并且卡片 JSON 本身要配置 callback 行为。
4. 常规流式输出请使用 `channel.stream()`。手写 CardKit patch 循环时，`sequence` 必须严格递增。
5. webhook 集成必须先初始化 Channel，再调用 `handle_webhook_request(...)`。
