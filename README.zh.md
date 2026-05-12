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

## Channel 模块

`lark_oapi.channel` 是基于 OpenAPI Client 和事件传输封装的高层模块。它把机器人接入中的事件监听、消息归一化、安全策略、出站发送、媒体上传下载、卡片交互、流式回复等能力收敛到 `FeishuChannel` 一个入口。

当你要开发会话式机器人，需要处理归一化消息、回复消息、媒体、卡片回调、@ 策略、WebSocket 长连接或 webhook 回调时，优先使用 Channel。

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

Channel 完整文档：

- [Channel 模块](./doc/channel.zh.md)
- [Channel 快速开始（英文）](./doc/channel/quickstart.md)
- [Channel API 参考（英文）](./doc/channel/reference.md)
- [可运行 echo bot 示例](./samples/channel/echo_bot.py)

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
