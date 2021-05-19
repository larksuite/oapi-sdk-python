[**README of Larksuite(Overseas)**](README.md) | 飞书

# 飞书开放接口SDK

## 概述

---

- 飞书开放平台，便于企业应用与飞书集成，让协同与管理更加高效，[概述](https://open.feishu.cn/document/uQjL04CN/ucDOz4yN4MjL3gzM)

- 飞书开发接口SDK，便捷调用服务端API与订阅服务端事件，例如：消息&群组、通讯录、日历、视频会议、云文档、 OKR等具体可以访问 [飞书开放平台文档](https://open.feishu.cn/document/) 看看【服务端
  API】。

## 问题反馈

--- 
如有任何SDK使用相关问题，请提交 [Github Issues](https://github.com/larksuite/oapi-sdk-python/issues), 我们会在收到 Issues 的第一时间处理，并尽快给您答复。


## 运行环境

---

- python 2.7及以上

## 安装方法

---

**最新的版本，请看** [pypi.org](https://pypi.org/project/larksuite-oapi/) 。

```shell
pip install larksuite-oapi==1.0.19
```

## 术语解释

- 飞书（FeiShu）：Lark在中国的称呼，主要为国内的企业提供服务，拥有独立的[域名地址](https://www.feishu.cn)。
- LarkSuite：Lark在海外的称呼，主要为海外的企业提供服务，拥有独立的[域名地址](https://www.larksuite.com/) 。
- 开发文档：开放平台的开放接口的参考，**开发者必看，可以使用搜索功能，高效的查询文档**。[更多介绍说明](https://open.feishu.cn/document/) 。
- 开发者后台：开发者开发应用的管理后台，[更多介绍说明](https://open.feishu.cn/app/) 。
- 企业自建应用：应用仅仅可在本企业内安装使用，[更多介绍说明](https://open.feishu.cn/document/uQjL04CN/ukzM04SOzQjL5MDN) 。
- 应用商店应用：应用会在 [应用目录](https://app.feishu.cn/?lang=zh-CN)
  展示，各个企业可以选择安装，[更多介绍说明](https://open.feishu.cn/document/uQjL04CN/ugTO5UjL4kTO14CO5kTN) 。

![App type](doc/app_type.zh.png)

## 快速使用

---

### 调用服务端API

- **必看** [如何调用服务端API](https://open.feishu.cn/document/ukTMukTMukTM/uYTM5UjL2ETO14iNxkTN/guide-to-use-server-api)
  ，了解调用服务端API的过程及注意事项。
    -
  由于SDK已经封装了app_access_token、tenant_access_token的获取，所以在调业务API的时候，不需要去获取app_access_token、tenant_access_token。如果业务接口需要使用user_access_token，需要进行设置（request.SetUserAccessToken("
  UserAccessToken")），具体请看 README.zh.md -> 如何构建请求（Request）
- 更多示例，请看：[sample/api/api.py](sample/api/api.py)（含：文件的上传与下载）

#### 使用`企业自建应用`访问 发送文本消息API 示例

- 有些老版接口，没有直接可以使用的SDK，可以使用`原生`模式。

```python
from larksuiteoapi.api import Request, set_timeout

from larksuiteoapi import Config, ACCESS_TOKEN_TYPE_TENANT, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


def test_send_message():
    body = {
        "user_id": "77bbc392",
        "msg_type": "text",
        "content": {
            "text": "test send message",
        }
    }

    req = Request('message/v4/send', 'POST', ACCESS_TOKEN_TYPE_TENANT, body, request_opts=[set_timeout(3)])
    resp = req.do(conf)
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data)
    else:
        print(resp.msg)
        print(resp.error)


if __name__ == '__main__':
    test_send_message()

```

#### 使用`企业自建应用`访问 修改用户部分信息API 示例

- 该接口是新的接口（请看"README.zh.md -> 已生成SDK的业务服务"），可以直接使用SDK。

```python
# -*- coding: UTF-8 -*-

from larksuiteoapi.service.contact.v3 import Service as ContactV3Service, User

from larksuiteoapi import Config, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
from src.larksuiteoapi.service.contact.v3 import User

app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)

# 通讯录V3版本服务
service = ContactV3Service(conf)


def test_user_patch():
    user = User()
    user.name = "rename"
    resp = service.users.patch(user).set_user_id("77bbc392").set_user_id_type("user_id").do()
    print('request id = %s' % resp.get_request_id())
    print(resp.code)
    if resp.code == 0:
        print(resp.data.user)
    else:
        print(resp.msg)
        print(resp.error)


if __name__ == '__main__':
    test_user_patch()
```

#### [使用`应用商店应用`调用 服务端API 示例](doc/ISV.APP.README.zh.md)

### 订阅服务端事件

- **必看** [订阅事件概述](https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM) ，了解订阅事件的过程及注意事项。
- 更多使用示例，请看[sample/event](sample/event)（含：结合flask的使用）

#### 使用`企业自建应用` 订阅 [首次启用应用事件](https://open.feishu.cn/document/ukTMukTMukTM/uQTNxYjL0UTM24CN1EjN) 示例

- 有些老的事件，没有直接可以使用的SDK，可以使用`原生`模式

```python

from larksuiteoapi.event import handle_event, set_event_callback
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


def app_open_event_handle(ctx, conf, event):
    # type: (Context, Config, dict) -> None
    print(ctx.get_request_id())
    print(conf.app_settings)
    print(event)


# set event type 'app_status_change' handle
set_event_callback(conf, 'app_open', app_open_event_handle)

app = Flask(__name__)


@app.route('/webhook/event', methods=['GET', 'POST'])
def webhook_event():
    oapi_request = OapiRequest(uri=request.path, body=request.data, header=OapiHeader(request.headers))
    resp = make_response()
    oapi_resp = handle_event(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.data = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


# 设置 "开发者后台" -> "事件订阅" 请求网址 URL：https://domain/webhook/event
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")


```

#### 使用`企业自建应用`订阅 [用户数据变更事件](https://open.feishu.cn/document/ukTMukTMukTM/uITNxYjLyUTM24iM1EjN#70402aa) 示例

- 该接口是新的事件，可以直接使用SDK

```python
# -*- coding: UTF-8 -*-

from larksuiteoapi.event import handle_event
from larksuiteoapi.service.contact.v3 import UserUpdatedEventHandler, UserUpdatedEvent
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


def user_update_handle(ctx, conf, event):
    # type: (Context, Config, UserUpdatedEvent) ->None
    print(ctx.get_request_id())
    print(event.header)
    print(event.event)
    pass


# set event type 'contact.user.updated_v3' handle
UserUpdatedEventHandler.set_callback(conf, user_update_handle)

app = Flask(__name__)


@app.route('/webhook/event', methods=['GET', 'POST'])
def webhook_event():
    oapi_request = OapiRequest(uri=request.path, body=request.data, header=OapiHeader(request.headers))
    resp = make_response()
    oapi_resp = handle_event(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.data = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


# 设置 "开发者后台" -> "事件订阅" 请求网址 URL：https://domain/webhook/event
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")

```

### 处理消息卡片回调

- **必看** [消息卡片开发流程](https://open.feishu.cn/document/ukTMukTMukTM/uAzMxEjLwMTMx4CMzETM) ，了解订阅事件的过程及注意事项
- 更多使用示例，请看：[sample/card](sample/card) （含：结合gin的使用）

#### 使用`企业自建应用`处理消息卡片回调示例

```python

from typing import Any, Union, Dict

from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

from larksuiteoapi.card import Card, set_card_callback, handle_card

from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

# 企业自建应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# 当前访问的是飞书，使用默认存储、默认日志（Debug级别），更多可选配置，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, DefaultLogger(), LEVEL_DEBUG)


# 设置消息卡片的处理
# 返回值：可以为None、新的消息卡片的Json（dict）
def handle(ctx, conf, card):
    # type: (Context, Config, Card) -> Union[None, Dict]
    print('card = %s' % card)
    return {
        "config": {
            "wide_screen_mode": True
        },
        "card_link": {
            "url": "https://www.baidu.com",
            "android_url": "https://developer.android.com/",
            "ios_url": "https://developer.apple.com/",
            "pc_url": "https://www.windows.com"
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "this is header"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "This is a very very very very very very very long text;"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "Read"
                        },
                        "type": "default"
                    }
                ]
            }
        ]
    }


set_card_callback(conf, handle)
app = Flask(__name__)


@app.route('/webhook/card', methods=['POST'])
def webhook_card():
    oapi_request = OapiRequest(uri=request.path, body=request.data, header=OapiHeader(request.headers))
    resp = make_response()
    oapi_resp = handle_card(conf, oapi_request)
    resp.headers['Content-Type'] = oapi_resp.content_type
    resp.data = oapi_resp.body
    resp.status_code = oapi_resp.status_code
    return resp


# 设置 "开发者后台" -> "应用功能" -> "机器人" 消息卡片请求网址：https://domain/webhook/card
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")

```    

## 高级使用

---

### 如何构建应用配置（AppSettings）

```python
from larksuiteoapi import Config

# 防止应用信息泄漏，配置环境变量中，变量（4个）说明：
# APP_ID："开发者后台" -> "凭证与基础信息" -> 应用凭证 App ID
# APP_SECRET："开发者后台" -> "凭证与基础信息" -> 应用凭证 App Secret
# VERIFICATION_TOKEN："开发者后台" -> "事件订阅" -> 事件订阅 Verification Token
# ENCRYPT_KEY："开发者后台" -> "事件订阅" -> 事件订阅 Encrypt Key
# 企业自建应用的配置，通过环境变量获取应用配置
app_settings = Config.new_internal_app_settings_from_env()
# 应用商店应用的配置，通过环境变量获取应用配置
app_settings = Config.new_isv_app_settings_from_env()

# 参数说明：
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（App ID、App Secret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（Verification Token、Encrypt Key）
# 企业自建应用的配置
app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
# 应用商店应用的配置
app_settings = Config.new_isv_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")

```

### 如何构建整体配置（Config）

- 访问 飞书、LarkSuite或者其他domain
- 应用的配置
- 日志（Logger）的实现，用于输出SDK处理过程中产生的日志，便于排查问题。
- 存储（Store）的实现，用于保存访问凭证（app/tenant_access_token）、临时凭证(app_ticket）
    - 推荐使用Redis实现，请看示例代码：[sample/config/config.py](sample/config/config.py) 的 RedisStore
        - 减少获取 访问凭证 的次数，防止调用访问凭证 接口被限频。
        - 应用商店应用，接受开放平台下发的 `app_ticket` ，会保存到存储中，所以存储（Store）的实现需要支持分布式存储。

```python
from larksuiteoapi import Config, AppSettings, \
    Logger, DefaultLogger, LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARN, LEVEL_ERROR, \
    DOMAIN_FEISHU, DOMAIN_LARK_SUITE

# for Cutome APP（企业自建应用）
app_settings = Config.new_internal_app_settings_from_env()

# 方法一，推荐使用Redis实现存储（Store），减少访问获取AccessToken接口的次数，请看示例：[RedisStore](sample/config/config.py)
# 参数说明：
# domain：DOMAIN_FEISHU / DOMAIN_LARK_SUITE / 其他域名地址
# app_settings：应用配置
# logger：[Logger](src/larksuiteoapi/logger.py)
# log_level：输出的日志级别 LEVEL_DEBUG/LEVEL_INFO/LEVEL_WARN/LEVEL_ERROR
# store: [Store](src/larksuiteoapi/store.py)，用来存储 app_ticket/access_token
conf = Config.new_config(DOMAIN_FEISHU, app_settings, logger, log_level, store)

# 方法二，使用默认的存储（Store）的实现，适合轻量的使用（不合适：应用商店应用 或 调用服务端API次数频繁）
# 参数说明：
# domain：DOMAIN_FEISHU / DOMAIN_LARK_SUITE / 其他域名地址
# app_settings：应用配置
# logger：[Logger](src/larksuiteoapi/logger.py)
# log_level：输出的日志级别 LEVEL_DEBUG/LEVEL_INFO/LEVEL_WARN/LEVEL_ERROR
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, logger, log_level)

```

### 如何构建请求（Request）

- 有些老版接口，没有直接可以使用的SDK，可以使用原生模式，这时需要构建请求。
- 更多示例，请看：[sample/api/api.py](sample/api/api.py)（含：文件的上传与下载）

```python

from larksuiteoapi import ACCESS_TOKEN_TYPE_APP, ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER
from larksuiteoapi.api import Request, FormData, FormDataFile, \
    set_path_params, set_query_params, set_timeout, set_no_data_field, \
    set_user_access_token, set_tenant_key, set_is_response_stream, set_response_stream


# 参数说明：
# http_path：API路径（`open-apis/`之后的路径），例如：https://domain/open-apis/contact/v3/users/:user_id，则 httpPath："contact/v3/users/:user_id"
# http_Method: GET/POST/PUT/BATCH/DELETE
# access_token_type：API使用哪种访问凭证，取值范围：ACCESS_TOKEN_TYPE_APP, ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER
# request_body：请求体（可能是 FormData()（例如：文件上传））,如果不需要请求体（例如一些GET请求），则传：nil
# request_opts：请求选项，一些不常用的参数封装，如下：
    # set_path_params({"user_id": 4})：设置URL Path参数（有:前缀）值，当httpPath="contact/v3/users/:user_id"时，请求的URL="https://{domain}/open-apis/contact/v3/users/4"
    # set_query_params({"age":4,"types":[1,2]})：设置 URL query，会在url追加?age=4&types=1&types=2
    # set_is_response_stream()，设置响应是否是流，response.data = bytes(文件内容)
    # set_response_stream(IO[any])，设置响应是否是流且响应流写入目标IO，response.data = 目标IO
    # set_no_data_field,设置响应的是否 没有`data`字段，业务接口都是有`data`字段，所以不需要设置
    # set_tenant_key，以`应用商店应用`身份，表示使用`tenant_access_token`访问API，需要设置
    # set_user_access_token，表示使用`user_access_token`访问API，需要设置
    # set_timeout，设置请求超时时间（单位：秒）

# (str, str, str, Any, T, List[Callable[[Option], Any]]) -> None
req = Request(http_path, http_Method, access_token_type, request_body, request_opts=None)

```

### 请求上下文（Context）及常用方法

```python

from larksuiteoapi import Context

ctx = Context()

# 获取请求的Request ID，便于排查问题
request_id = ctx.get_request_id()

# 获取请求的响应状态码
status_code = ctx.get_http_status_code()

```

### 如何发送请求

- 由于SDK已经封装了app_access_token、tenant_access_token的获取，所以在调业务API的时候，不需要去获取app_access_token、tenant_access_token。如果业务接口需要使用user_access_token，需要进行设置（request.SetUserAccessToken("
UserAccessToken")），具体请看 README.zh.md -> 如何构建请求（Request）

- 更多使用示例，请看：[sample/api/api.py](sample/api/api.py)

```python

from larksuiteoapi.api import Request

req = Request(...)

# 发送请求
# 参数说明：
# conf：整体的配置（Config）
# 返回值说明：
# Response：请求的结果（= http response body）
resp = req.do(conf)

print('request id = %s' % resp.get_request_id())
print(resp.code)
if resp.code == 0:
    print(resp.data.message_id)
else:
    print(resp.msg)
    print(resp.error)

```

## 已生成SDK的业务服务

---

|业务域|版本|路径|代码示例|
|---|---|---|----|
|[用户身份验证](https://open.feishu.cn/document/ukTMukTMukTM/uETOwYjLxkDM24SM5AjN)|v1|[service/authen](src/larksuiteoapi/service/authen)|[sample/api/authen_service.py](sample/api/authen_service.py)|
|[图片](https://open.feishu.cn/document/ukTMukTMukTM/uEDO04SM4QjLxgDN)|v4|[service/image](src/larksuiteoapi/service/image)|[sample/api/image_service.py](sample/api/image_service.py)|
|[通讯录](https://open.feishu.cn/document/ukTMukTMukTM/uETNz4SM1MjLxUzM/v3/introduction)|v3|[service/contact](src/larksuiteoapi/service/contact)|[sample/api/contact_service.py](sample/api/contact_service.py)|
|[日历](https://open.feishu.cn/document/ukTMukTMukTM/uETM3YjLxEzN24SMxcjN)|v4|[service/calendar](src/larksuiteoapi/service/calendar)|[sample/api/calendar_service.py](sample/api/calendar_service.py)|

## License

---

- MIT

## 联系我们

---

- 飞书：[服务端SDK](https://open.feishu.cn/document/ukTMukTMukTM/uETO1YjLxkTN24SM5UjN) 页面右上角【这篇文档是否对你有帮助？】提交反馈


