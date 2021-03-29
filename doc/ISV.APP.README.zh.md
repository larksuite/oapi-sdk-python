# 使用应用商店应用调用服务端API

---

- 如何获取app_access_token，请看：[获取app_access_token](https://open.feishu.cn/document/ukTMukTMukTM/uEjNz4SM2MjLxYzM) （应用商店应用）
    - 与企业自建应用相比，应用商店应用的获取app_access_token的流程复杂一些。
        - 需要开放平台下发的app_ticket，通过订阅事件接收。SDK已经封装了app_ticket事件的处理，只需要启动事件订阅服务。
        - 使用SDK调用服务端API时，如果当前还没有收到开发平台下发的app_ticket，会报错且向开放平台申请下发app_ticket，可以尽快的收到开发平台下发的app_ticket，保证再次调用服务端API的正常。
        - 使用SDK调用服务端API时，需要使用tenant_access_token访问凭证时，需要 tenant_key ，来表示当前是哪个租户使用这个应用调用服务端API。
            - tenant_key，租户安装启用了这个应用，开放平台发送的服务端事件，事件内容中都含有tenant_key。

### 使用`应用商店应用`访问 [发送文本消息API](https://open.feishu.cn/document/ukTMukTMukTM/uUjNz4SN2MjL1YzM) 示例

- 第一步：启动启动事件订阅服务，用于接收`app_ticket`。

```python
from larksuiteoapi.event import handle_event
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, DOMAIN_FEISHU

# 应用商店应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_isv_app_settings_from_env("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_isv_app_settings_from_env()

# 当前访问的是飞书，使用redis store，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config(DOMAIN_FEISHU, app_settings, app_settings, logger, log_level, store)

app = Flask(__name__)

@app.route('/webhook/event', methods=['POST'])
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

- 第二步：调用服务端接口，有些老版接口，没有直接可以使用的SDK，可以使用`原生`模式。

```python
# -*- coding: UTF-8 -*-

from larksuiteoapi.api import Request, set_timeout, set_tenant_key

from larksuiteoapi import Config, ACCESS_TOKEN_TYPE_TENANT, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 应用商店应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_isv_app_settings_from_env("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_isv_app_settings_from_env()

# 当前访问的是飞书，使用redis store，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config(DOMAIN_FEISHU, app_settings, app_settings, logger, log_level, store)


def test_send_message():
    body = {
        "user_id": "77bbc392",
        "msg_type": "text",
        "content": {
            "text": "test send message",
        }
    }
    # 构建请求 && 设置企业标识（tenant_key）
    req = Request('message/v4/send', 'POST', ACCESS_TOKEN_TYPE_TENANT, body,
                  request_opts=[set_tenant_key("Tenant key"), set_timeout(3)])
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

## 使用`应用商店应用`访问 [修改用户部分信息API](https://open.feishu.cn/document/contact/v3/user/patch) 示例

- 第一步：略，同上

- 第二步：调用服务端接口，该接口是新的接口（请看"README.zh.md -> 已生成SDK的业务服务"），可以直接使用SDK。

```python
from larksuiteoapi.service.contact.v3 import Service as ContactV3Service, User

from larksuiteoapi import Config, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# 应用商店应用的配置
# AppID、AppSecret: "开发者后台" -> "凭证与基础信息" -> 应用凭证（AppID、AppSecret）
# VerificationToken、EncryptKey："开发者后台" -> "事件订阅" -> 事件订阅（VerificationToken、EncryptKey）
# app_settings = Config.new_isv_app_settings_from_env("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_isv_app_settings_from_env()

# 当前访问的是飞书，使用redis store，请看：README.zh.md->高级使用->如何构建整体配置（Config）。
conf = Config(DOMAIN_FEISHU, app_settings, app_settings, logger, log_level, store)

# 通讯录V3版本服务
service = ContactV3Service(conf)


def test_user_patch():
    user = User()
    user.name = "rename"
    # 构建请求 && 设置租户标识（tenant_key）&& 发送请求
    resp = service.users.patch(user, tenant_key='Tenant Key').set_user_id("77bbc392").set_user_id_type("user_id").do()
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
