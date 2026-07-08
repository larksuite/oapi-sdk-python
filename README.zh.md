# 飞书开放接口 SDK

[English](./README.md)

飞书开放平台提供消息、通讯录、审批、电子表格、多维表格等服务端开放能力。实际接入时，开发者通常还需要处理 token 获取与维护、数据加解密、请求签名校验、事件分发、请求和响应模型等通用工作。本 SDK 将这些逻辑封装在统一的 Python 接口中，降低接入成本。

## 介绍文档

- [开发前准备（安装 SDK）](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development)
- [调用服务端 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/invoke-server-api)
- [处理事件订阅](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/handle-events)
- [处理卡片回调](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/handle-callbacks)
- [常见问题](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/faq)

## 安装

```bash
pip install lark-oapi
```

要求 Python 3.8 或更高版本。

## 基础用法

```python
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

client = lark.Client.builder() \
    .app_id("cli_xxx") \
    .app_secret("your_app_secret") \
    .build()

request = CreateMessageRequest.builder() \
    .receive_id_type("chat_id") \
    .request_body(CreateMessageRequestBody.builder()
        .receive_id("oc_xxx")
        .msg_type("text")
        .content("{\"text\":\"hello world\"}")
        .build()) \
    .build()

response = client.im.v1.message.create(request)
```

## ClientAssertion 无密钥模式

自建应用如果通过外部签发服务提供 `client_assertion`，SDK 可以在不配置
`app_secret` 的情况下换取 tenant token。SDK 不生成、不解析、不签名 JWT，
也不保存私钥；provider 只需要返回最终的 assertion 字符串。

```python
import os

import lark_oapi as lark
from lark_oapi.core.client_assertion import ClientAssertionToken


class EnvClientAssertionProvider:
    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        return ClientAssertionToken(os.environ["LARK_CLIENT_ASSERTION"])


client = lark.Client.builder() \
    .app_id(os.environ["LARK_APP_ID"]) \
    .client_assertion_provider(EnvClientAssertionProvider()) \
    .build()
```

如果使用自定义 OpenAPI 域名，需要同时配置 `oauth_base_url(...)`，以便 SDK
正确生成 OAuth audience。无密钥模式仅支持自建应用，不支持只依赖
AppAccessToken 的 API。

## Channel 模块
## 一键创建应用

`lark_oapi.register_app` 基于 OAuth device flow 创建应用。SDK 会在
`on_qr_code` 回调中返回验证链接，你可以将该链接渲染为二维码，或直接展示给用户在飞书/Lark 中打开。

```python
import lark_oapi as lark


def on_qr_code(info):
    print(info["url"])


result = lark.register_app(
    on_qr_code=on_qr_code,
    app_preset={
        "avatar": [
            "https://example.com/a.png",
            "https://example.com/b.webp",
        ],
        "name": "{user}的应用",
        "desc": "由业务平台自动生成",
    },
)

print(result["client_id"])
```

### 自定义权限/事件/回调与更新已有应用

创建应用时，可通过 `addons` 在平台基础模板上增量申请权限、事件订阅和回调。这些配置会预填到用户扫码后的确认页中，用户确认后生效：

```python
result = lark.register_app(
    on_qr_code=on_qr_code,
    addons={
        "scopes": {
            "tenant": ["im:message:send_as_bot"],
            "user": ["calendar:calendar:read"],
        },
        "events": {"items": {"tenant": ["im.message.receive_v1"]}},
        "callbacks": {"items": ["card.action.trigger"]},
    },
    create_only=True,
)

lark.register_app(
    on_qr_code=on_qr_code,
    app_id="cli_xxx",
    addons={"scopes": {"tenant": ["drive:drive.metadata:readonly"]}},
)
```

注意：

- `addons` 仅支持在基础模板上增量叠加，不支持删减基础权限。
- `addons.preset` 控制底座模板：缺省或 `True` 使用默认底座模板；`False` 切换为最小基础模板，最终配置只包含 `addons` 显式声明的内容。传 `"preset": False` 时，`addons` 可以不带任何增量条目。
- 仅支持 5 类公开配置：应用/用户身份权限、应用/用户身份事件、回调。敏感配置（事件请求地址、`security.*`、加密 key 等）不能通过 `addons` 传入。
- SDK 只校验数据形状，不校验权限点/事件/回调名称是否存在；平台目录中不存在的名称会被确认页忽略。

如需不使用 mock、真实跑一遍手动 E2E：

```bash
python3 samples/registration/app_preset_live_e2e.py --open
```

### `register_app` 参数

| 参数 | 描述 | 类型 | 必填 | 默认值 |
| ---- | ---- | ---- | ---- | ---- |
| `on_qr_code` | 验证链接就绪时的回调，参数为 `{"url": str, "expire_in": int}` | function | 是 | - |
| `on_status_change` | 轮询状态变化回调，状态包括 `polling`、`slow_down`、`domain_switched` | function | 否 | - |
| `source` | 来源标识，会拼入二维码 URL 的 `source` 参数，格式为 `python-sdk/{source}` | string | 否 | `python-sdk` |
| `cancel_event` | 用于取消同步轮询的 `threading.Event` | threading.Event | 否 | - |
| `domain` | 自定义飞书账号域名 base URL | string | 否 | `https://accounts.feishu.cn` |
| `lark_domain` | 自定义 Lark 账号域名 base URL，检测到 Lark 租户时使用 | string | 否 | `https://accounts.larksuite.com` |
| `app_preset` | 创建页预填信息。所有字段都是选填，用户扫码后仍可在页面手动修改。调用方传原始值，SDK 自动 URL Encode | dict | 否 | - |
| `app_preset.avatar` | 应用头像 URL，支持 1-6 个；传多个时默认选中第一个。图片格式由 Web 页面处理：png / jpg / jpeg / webp / gif | string 或 list[string] | 否 | - |
| `app_preset.name` | 应用名称，支持 `{user}` 占位符，由 Web 页面替换为扫码用户名称 | string | 否 | - |
| `app_preset.desc` | 应用描述，支持 `{user}` 占位符 | string | 否 | - |
| `addons` | 增量权限/事件/回调配置，预填到扫码后的确认页，用户确认后生效 | dict | 否 | - |
| `addons.preset` | 底座模板开关。缺省或 `True` 使用默认底座模板；`False` 切换为最小基础模板，应用配置完全由 `addons` 显式声明 | bool | 否 | `True` |
| `addons.scopes.tenant` | 应用身份权限列表，如 `im:message:send_as_bot` | list[string] | 否 | - |
| `addons.scopes.user` | 用户身份权限列表，如 `calendar:calendar:read` | list[string] | 否 | - |
| `addons.events.items.tenant` | 应用身份事件列表，如 `im.message.receive_v1` | list[string] | 否 | - |
| `addons.events.items.user` | 用户身份事件列表，如 `calendar.calendar.event.changed_v4` | list[string] | 否 | - |
| `addons.callbacks.items` | 回调列表，如 `card.action.trigger` | list[string] | 否 | - |
| `create_only` | 为 `True` 时落地页仅允许创建新应用，隐藏「选择已有应用」入口。与 `app_id` 同时传入时优先级更高 | bool | 否 | - |
| `app_id` | 已有应用的 App ID（`cli_` 开头）。传入后流程变为更新该应用配置；二维码 URL 上使用平台参数 `clientID` | string | 否 | - |

## 旧版 Channel 模块

`lark_oapi.channel` 是迁移窗口内为了兼容保留的旧版 Channel 入口。新的 Channel 能力只进入 [`lark-channel-sdk`](https://pypi.org/project/lark-channel-sdk/)，并使用 `lark_channel` import path；现有 `lark_oapi.channel` 用户的关键缺陷修复会评估是否回迁，维护窗口截止到 2027-06-02。

`lark-channel-sdk` 可以和 `lark-oapi` 同时安装。独立包的 [`SecurityConfig`](https://github.com/larksuite/channel-sdk-python/blob/main/docs/security.md) 默认使用兼容模式，便于迁移后的机器人先用 audit 模式观测，再切到 strict 模式强制安全检查。完整步骤见 [迁移手册](https://github.com/larksuite/channel-sdk-python/blob/main/docs/migration-from-lark-oapi.md)。

```bash
pip install lark-channel-sdk
```

```python
from lark_channel import FeishuChannel
```

旧版 import 示例：

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

Channel 文档：

- [旧版 Channel 模块](./doc/channel.zh.md)
- [旧版 Channel 快速开始（英文）](./doc/channel/quickstart.md)
- [旧版 Channel API 参考（英文）](./doc/channel/reference.md)
- [独立 Channel 迁移手册](https://github.com/larksuite/channel-sdk-python/blob/main/docs/migration-from-lark-oapi.md)
- [独立 Channel 安全配置](https://github.com/larksuite/channel-sdk-python/blob/main/docs/security.md)
- [可运行旧版 echo bot 示例](./samples/channel/echo_bot.py)

## 扩展示例

更多组合 API 和业务场景示例见 [oapi-sdk-python-demo](https://github.com/larksuite/oapi-sdk-python-demo)。

- [发送文件消息](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/im/send_file.py)
- [发送图片消息](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/im/send_image.py)
- [获取部门下所有用户列表](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/contact/list_user_by_department.py)
- [创建多维表格同时添加数据表](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/base/create_app_and_tables.py)
- [机器人自动拉群报警](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/quick_start/robot)

## 许可协议

MIT

## 加入交流互助群

[_单击_](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=575k28fa-2c12-400a-80c0-2d8924e00d38)或扫码加入讨论群。

<img src="doc/qrcode.png" width="200" alt="讨论群">
