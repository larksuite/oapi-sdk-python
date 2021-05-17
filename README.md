[**飞书，点这里**](README.zh.md) | Larksuite(Overseas)

- 如果使用的是飞书，请看 [**飞书，点这里**](README.zh.md) ，飞书与Larksuite使用的域名不一样，引用的文档地址也是不同的。(If you are using FeiShu, please see [**飞书，点这里**](README.zh.md) , Feishu and larksuite use different domain names and reference different document addresses.)

# LarkSuite open api SDK

## Overview

---

- Larksuite open platform facilitates the integration of enterprise applications and larksuite, making collaboration and
  management more efficient.

- Larksuite development interface SDK, convenient call server API and subscribe server events, such as: Message & group,
  address book, calendar, docs and others can
  visit [larksuite open platform document](https://open.larksuite.cn/document) ,Take a look at [REFERENCE].

## Run environment

---

- python 2.7+

## Install

**Latest version, see** [pypi.org](https://pypi.org/project/larksuite-oapi/) .

---

```shell
pip install larksuite-oapi==1.0.19
```

## Explanation of terms

- Larksuite: the overseas name of lark, which mainly provides services for overseas enterprises and has an
  independent [domain name address](https://www.larksuite.com/) .
- Development documents: reference to the open interface of the open platform **developers must see, and can use search
  to query documents efficiently** . [more information](https://open.feishu.cn/document/) .
- Developer background: the management background for developers to develop
  applications, [more introduction](https://open.larksuite.cn/app/) .
- Cutome APP: the application can only be installed and used in the
  enterprise，[more introduction](https://open.larksuite.com/document/ukzMxEjL5MTMx4SOzETM/uEjNwYjLxYDM24SM2AjN) .
- Marketplace App: The app will be displayed in [App Directory](https://app.larksuite.com/) Display, each enterprise can
  choose to install.

![App type](doc/app_type.en.png)

## Quick use

---

### Call API

#### Example of using "Custom App" to access [send text message](https://open.larksuite.com/document/uMzMyEjLzMjMx4yMzITM/ugDN0EjL4QDNx4CO0QTM) API

- Since the SDK has encapsulated the app_access_token、tenant_access_token So when calling the business API, you don't
  need to get the app_access_token、tenant_access_token. If the business interface needs to use user_access_token, which
  needs to be set（request.SetUserAccessToken("user_access_token")), Please refer to README.md -> How to build a request(
  Request)
- Some of the old API do not have a direct SDK to use. They can use the `native` mode.

```python
from larksuiteoapi.api import Request, set_timeout

from larksuiteoapi import Config, ACCESS_TOKEN_TYPE_TENANT, DOMAIN_LARK_SUITE, DOMAIN_FEISHU, DefaultLogger, LEVEL_DEBUG

# Configuration of "Custom App", parameter description:
# AppID、AppSecret: "Developer Console" -> "Credentials"（App ID、App Secret）
# VerificationToken、EncryptKey: "Developer Console" -> "Event Subscriptions"（Verification Token、Encrypt Key）	
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# Currently, you are visiting larksuite, which uses default storage and default log (debug level). More optional configurations are as follows: README.md->Advanced use->How to build overall configuration(Config)。
conf = Config.new_config_with_memory_store(DOMAIN_LARK_SUITE, app_settings, DefaultLogger(), LEVEL_DEBUG)


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

### Subscribe to events

- [Subscribe to events](https://open.larksuite.com/document/uMzMyEjLzMjMx4yMzITM/uETM4QjLxEDO04SMxgDN), to understand
  the process and precautions of subscribing to events.
- For more use examples, please refer to [sample/event](sample/event)（including: use in combination with flask）

#### Example of using "Custom App" to subscribe [App First Enabled](https://open.larksuite.com/document/uMzMyEjLzMjMx4yMzITM/uYjMyYjL2IjM24iNyIjN) event.

- For some old events, there is no SDK that can be used directly. You can use the `native` mode

```python

from larksuiteoapi.event import handle_event, set_event_callback
from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

from larksuiteoapi import Config, Context, DOMAIN_FEISHU,DOMAIN_LARK_SUITE,  DefaultLogger, LEVEL_DEBUG

# Configuration of "Custom App", parameter description:
# AppID、AppSecret: "Developer Console" -> "Credentials"（App ID、App Secret）
# VerificationToken、EncryptKey: "Developer Console" -> "Event Subscriptions"（Verification Token、Encrypt Key）	
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# Currently, you are visiting larksuite, which uses default storage and default log (debug level). More optional configurations are as follows: README.md->Advanced use->How to build overall configuration(Config)。
conf = Config.new_config_with_memory_store(DOMAIN_LARK_SUITE, app_settings, DefaultLogger(), LEVEL_DEBUG)


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


# Start the httpserver, "Developer Console" -> "Event Subscriptions", setting Request URL: https://domain/webhook/event
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")

```

### Processing message card callbacks

- [Message Card Development Process](https://open.larksuite.com/document/uMzMyEjLzMjMx4yMzITM/ukzM3QjL5MzN04SOzcDN) , to
  understand the process and precautions of processing message cards
- For more use examples, please refer to [sample/card](sample/card)（including: use in combination with flask）

#### Example of using "Custom App" to handling message card callback.

```python

from typing import Any, Union, Dict

from larksuiteoapi import Config, Context, DOMAIN_FEISHU, DOMAIN_LARK_SUITE, DefaultLogger, LEVEL_DEBUG

from larksuiteoapi.card import Card, set_card_callback, handle_card

from larksuiteoapi.model import OapiHeader, OapiRequest

from flask import Flask, request
from flask.helpers import make_response

# Configuration of "Custom App", parameter description:
# AppID、AppSecret: "Developer Console" -> "Credentials"（App ID、App Secret）
# VerificationToken、EncryptKey: "Developer Console" -> "Event Subscriptions"（Verification Token、Encrypt Key）	
# app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
app_settings = Config.new_internal_app_settings_from_env()

# Currently, you are visiting larksuite, which uses default storage and default log (debug level). More optional configurations are as follows: README.md->Advanced use->How to build overall configuration(Config)。
conf = Config.new_config_with_memory_store(DOMAIN_LARK_SUITE, app_settings, DefaultLogger(), LEVEL_DEBUG)


# Return value: can be None or JSON(dict) of new message card
def handle(ctx, conf, card):
    # type: (Context, Config, Card) -> Union[None, Dict]
    print('card = %s' % card)
    return {
        "config": {
            "wide_screen_mode": True
        },
        "card_link": {
            "url": "https://www.google.com",
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


# "Developer Console" -> "Features" -> "Bot", setting Message Card Request URL: https://domain/webhook/card
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=8089, host="0.0.0.0")


```    

## Advanced use

---

### How to build app settings(AppSettings)

```python
from larksuiteoapi import Config

# To prevent application information leakage, in the configuration environment variables, the variables (4) are described as follows:
# APP_ID: "Developer Console" -> "Credentials"（App ID）
# APP_Secret: "Developer Console" -> "Credentials"（App Secret）
# VERIFICATION_Token: VerificationToken、EncryptKey: "Developer Console" -> "Event Subscriptions"（Verification Token）
# ENCRYPT_Key: VerificationToken、EncryptKey: "Developer Console" -> "Event Subscriptions"（Encrypt Key）
# The configuration of "Custom App" is obtained through environment variables
app_settings = Config.new_internal_app_settings_from_env()
# The configuration of "Marketplace App" is obtained through environment variables
app_settings = Config.new_isv_app_settings_from_env()

# Parameter Description:
# AppID、AppSecret: "Developer Console" -> "Credentials"（App ID、App Secret）
# VerificationToken、EncryptKey: "Developer Console" -> "Event Subscriptions"（Verification Token、Encrypt Key）
# The configuration of "Custom App"
app_settings = Config.new_internal_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
# The configuration of "Marketplace App"
app_settings = Config.new_isv_app_settings("AppID", "AppSecret", "VerificationToken", "EncryptKey")
```

### How to build overall configuration(Config)

- Visit Larksuite, Feishu or others
- App settings
- The implementation of logger is used to output the logs generated in the process of SDK processing, which is
  convenient for troubleshooting.
- The implementation of store is used to save the access credentials (app/tenant_access_token), temporary voucher (
  app_ticket）
    - Redis is recommended. Please see the example code: [sample/config/config.py](sample/config/config.py) RedisStore
        - It can reduce the times of obtaining access credentials and prevent the frequency limit of calling access
          credentials interface.
        - "Marketplace App", accept open platform distributed `app_ticket` will be saved to the storage, so the
          implementation of the storage (store) needs to support distributed storage.

```python
from larksuiteoapi import Config, AppSettings, \
    Logger, DefaultLogger, LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARN, LEVEL_ERROR, \
    DOMAIN_FEISHU, DOMAIN_LARK_SUITE

# for Cutome APP
app_settings = Config.new_internal_app_settings_from_env()

# Method 1: it is recommended to use redis to implement the store interface, so as to reduce the times of accessing the access_token API: [RedisStore](sample/config/config.py)
# Parameter Description:
# domain: DOMAIN_FEISHU / DOMAIN_LARK_SUITE / URL domain address
# app_settings: AppSetting
# logger: [Logger](src/larksuiteoapi/logger.py)
# log_level: LEVEL_DEBUG/LEVEL_INFO/LEVEL_WARN/LEVEL_ERROR
# store: [Store](src/larksuiteoapi/store.py)，用来存储 app_ticket/access_token
conf = Config.new_config(DOMAIN_FEISHU, app_settings, logger, log_level, store)

# Method 2: use the implementation of the default storage interface (store), which is suitable for light-weight use (not suitable: "Marketplace App" applies or calls the server API frequently)
# 参数说明: 
# domain: DOMAIN_FEISHU / DOMAIN_LARK_SUITE / URL domain address
# app_settings: AppSetting
# logger: [Logger](src/larksuiteoapi/logger.py)
# log_level: LEVEL_DEBUG/LEVEL_INFO/LEVEL_WARN/LEVEL_ERROR
conf = Config.new_config_with_memory_store(DOMAIN_FEISHU, app_settings, logger, log_level)

```

### How to build a request(Request)

- Some of the old interfaces do not have an SDK that can be used directly. They can use `native` mode. At this time,
  they need to build requests.
- For more examples, see [sample/api/api.py](sample/api/api.py) (including: file upload and download)

```python
from larksuiteoapi import ACCESS_TOKEN_TYPE_APP, ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER
from larksuiteoapi.api import Request, FormData, FormDataFile, \
    set_path_params, set_query_params, set_timeout, set_no_data_field, \
    set_user_access_token, set_tenant_key, set_is_response_stream, set_response_stream


# Parameter Description:
# http_path: API path（the path after `open-apis/`）, for example: https://domain/open-apis/contact/v3/users/:user_id, then httpPath: "contact/v3/users/:user_id"
# http_Method: GET/POST/PUT/BATCH/DELETE
# access_token_type: What kind of access certificate does the API use and the value range: ACCESS_TOKEN_TYPE_APP, ACCESS_TOKEN_TYPE_TENANT, ACCESS_TOKEN_TYPE_USER
# request_body: Request body (possibly FormData()(e.g. file upload)), if the request body (e.g. some get requests) is not needed, it will be transferred to: None
# request_opts: Extension function, some rarely used parameter encapsulation, as follows:
    # set_path_params({"user_id": 4}): set the URL Path parameter(with: prefix) value, When httpPath="contact/v3/users/:user_id", the requested URL="https://{domain}/open-apis/contact/v3/users/4"
    # set_query_params({"age":4,"types":[1,2]}): Set the URL query, will append to the url?age=4&types=1&types=2   
    # set_is_response_stream(), set whether the response is a stream, response.data = bytes(file binary)
    # set_response_stream(IO[any]), set whether the response is a stream, such as downloading a file, response.data = IO[any]
    # set_no_data_field, set whether the response does not have a `data` field, business interfaces all have `data `Field, so you don’t need to set 
    # set_tenant_key, as an `app store application`, it means using `tenant_access_token` to access the API, you need to set
    # set_user_access_token, which means using` user_access_token` To access the API, you need to set 
    # set_timeou, set the request timeout (in seconds)

# (str, str, str, Any, T, List[Callable[[Option], Any]]) -> None
req = Request(http_path, http_Method, access_token_type, request_body, request_opts=None)
```

### Request context(Context) And common methods

```python
from larksuiteoapi import Context

ctx = Context()

# Get the request ID of the request for troubleshooting
request_id = ctx.get_request_id()

# Get the response status code of the request
status_code = ctx.get_http_status_code()

```

### How to send a request

- Since the SDK has encapsulated the app_access_token、tenant_access_token So when calling the business API, you don't
  need to get the app_access_token、tenant_access_token. If the business interface needs to use user_access_token, which
  needs to be set（request.SetUserAccessToken("user_access_token")), Please refer to README.md -> How to build a request(
  Request)
- For more use examples, please see: [sample/api/api.py](sample/api/api.py)

```python
from larksuiteoapi.api import Request

req = Request(...)

# Send Request
# Parameter Description:
# conf: Overall configuration（Config）
# Return value Description:
# Response: response（= http response body）
resp = req.do(conf)

print('request id = %s' % resp.get_request_id())
print(resp.code)
if resp.code == 0:
    print(resp.data.message_id)
else:
    print(resp.msg)
    print(resp.error)

```

## License

---

- MIT
