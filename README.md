# 飞书开放接口SDK/Feishu OpenPlatform Server SDK

旨在让开发者便捷的调用飞书开放API、处理订阅的事件、处理服务端推送的卡片行为等。

Feishu Open Platform offers a series of server-side atomic APIs to achieve diverse functionalities. However, actual coding requires additional work, such as obtaining and maintaining access tokens, encrypting and decrypting data, and verifying request signatures. Furthermore, the lack of semantic descriptions for function calls and type system support can increase coding burdens.

To address these issues, Feishu Open Platform has developed the Open Interface SDK, which incorporates all lengthy logic processes, provides a comprehensive type system, and offers a semantic programming interface to enhance the coding experience.

## 介绍文档 Introduction Documents

- [开发前准备（安装） / Preparations before development(Install SDK)](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development)
- [调用服务端 API / Calling Server-side APIs](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/invoke-server-api)
- [处理事件订阅 / Handle Events](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/handle-events)
- [处理卡片回调 / Handle Card Callbacks](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/handle-callbacks)
- [常见问题 / SDK FAQs](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/faq)

## 扩展示例
我们还基于 SDK 封装了常用的 API 组合调用及业务场景示例，如：
* 消息
  * [发送文件消息](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/im/send_file.py)
  * [发送图片消息](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/im/send_image.py)
* 通讯录
  * [获取部门下所有用户列表](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/contact/list_user_by_department.py)
* 多维表格
  * [创建多维表格同时添加数据表](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/base/create_app_and_tables.py)
* 电子表格
  * [复制粘贴某个范围的单元格数据](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/sheets/copy_and_paste_by_range.py)
  * [下载指定范围单元格的所有素材列表](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/sheets/download_media_by_range.py)
* 教程
  * [机器人自动拉群报警](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/quick_start/robot) ([开发教程](https://open.feishu.cn/document/home/message-development-tutorial/introduction))

更多示例可参考：https://github.com/larksuite/oapi-sdk-python-demo

## Channel module

`lark_oapi.channel` is a higher-level capability layer on top of the core
OpenAPI client. It wraps event subscription, message normalization, outbound
sending, streaming card updates, deduplication, retries, and SSRF-guarded
media uploads behind a single `FeishuChannel` class — so a working bot is
only a handful of lines.

### Install

```bash
pip install lark-oapi
```

### Quickstart — echo bot

```python
import asyncio
from lark_oapi.channel import FeishuChannel

channel = FeishuChannel(app_id="cli_xxx", app_secret="***")

@channel.on("message")
async def on_message(msg):
    await channel.send(
        msg.conversation.chat_id,
        {"text": f"echo: {msg.content_text}"},
    )

asyncio.run(channel.connect())
```

`channel.connect()` opens a long-lived WebSocket to Feishu, dispatches inbound
events through registered `on(...)` handlers, and keeps the connection alive
across reconnects. `channel.send(...)` accepts plain dicts (`{"text": ...}`,
`{"markdown": ...}`, `{"card": ...}`) or strongly-typed `Outbound*` payloads
from `lark_oapi.channel`.

See the [Channel quickstart](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/quickstart.md),
[Channel reference](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/reference.md),
and [Channel echo bot sample](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/samples/channel/echo_bot.py)
for runnable usage and API details. The public surface is exported from
[`lark_oapi.channel`](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/lark_oapi/channel/__init__.py).

## Requirements
Python >= 3.8

## License
MIT

## 加入交流互助群
[_单击_](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=575k28fa-2c12-400a-80c0-2d8924e00d38)或扫码加入讨论群

<img src="doc/qrcode.png" width="200" alt="讨论群">
