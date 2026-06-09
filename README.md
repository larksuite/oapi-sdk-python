# Feishu OpenPlatform Server SDK for Python

[中文](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/README.zh.md)

The Feishu Open Platform provides server-side APIs for messaging, contacts,
approval, sheets, Base, and many other product capabilities. This SDK wraps the
repeated platform work around API calls, including token management, request
signing, encryption/decryption, event dispatching, and typed request/response
models.

## Documentation

- [Preparations before development](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development)
- [Calling server-side APIs](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/invoke-server-api)
- [Handle events](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/handle-events)
- [Handle card callbacks](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/handle-callbacks)
- [SDK FAQs](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/faq)

## Installation

```bash
pip install lark-oapi
```

Python 3.8 or later is required.

## Basic Usage

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

## One-Click App Registration

`lark_oapi.register_app` creates an app through the OAuth device flow. It
returns a verification URL in `on_qr_code`; render the URL as a QR code or show
it as a link for the user to open in Feishu/Lark.

```python
import lark_oapi as lark

## ClientAssertion Keyless Mode

For self-built apps that use an external signing service, the SDK can fetch
tenant tokens with `client_assertion` instead of `app_secret`. The SDK does not
generate, parse, sign, or store JWT private keys; your provider supplies the
final assertion string.

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

If you use a custom OpenAPI domain, also configure `oauth_base_url(...)` so the
SDK can derive the OAuth audience correctly. Keyless mode is for self-built
apps only and does not support AppAccessToken-only APIs.

## Channel Module

def on_qr_code(info):
    print(info["url"])


result = lark.register_app(
    on_qr_code=on_qr_code,
    app_preset={
        "avatar": [
            "https://example.com/a.png",
            "https://example.com/b.webp",
        ],
        "name": "{user}'s app",
        "desc": "Created by the business platform",
    },
)

print(result["client_id"])
```

For a real manual E2E run without mocked registration responses:

```bash
python3 samples/registration/app_preset_live_e2e.py --open
```

### `register_app` parameters

| Parameter | Description | Type | Required | Default |
| ---- | ---- | ---- | ---- | ---- |
| `on_qr_code` | Callback when the verification URL is ready. Receives `{"url": str, "expire_in": int}` | function | Yes | - |
| `on_status_change` | Callback on polling status changes. Status values include `polling`, `slow_down`, `domain_switched` | function | No | - |
| `source` | Source identifier appended to the QR URL as `python-sdk/{source}` | string | No | `python-sdk` |
| `cancel_event` | `threading.Event` used to cancel sync polling | threading.Event | No | - |
| `domain` | Custom Feishu accounts base URL | string | No | `https://accounts.feishu.cn` |
| `lark_domain` | Custom Lark accounts base URL used when tenant brand is Lark | string | No | `https://accounts.larksuite.com` |
| `app_preset` | Pre-fill values for the app-creation page. All fields are optional; users can still edit them on the page. Pass raw values; the SDK URL-encodes them automatically | dict | No | - |
| `app_preset.avatar` | App avatar URL(s). 1-6 URLs supported; the first one is selected by default. Allowed formats are handled by the Web page: png / jpg / jpeg / webp / gif | string or list[string] | No | - |
| `app_preset.name` | App name. Supports the `{user}` placeholder, replaced by the Web page with the scanning user's name | string | No | - |
| `app_preset.desc` | App description. Supports the `{user}` placeholder | string | No | - |

## Legacy Channel Module

`lark_oapi.channel` is the legacy Channel entry point kept for compatibility
during the migration window. New Channel features ship in
[`lark-channel-sdk`](https://pypi.org/project/lark-channel-sdk/) with the
`lark_channel` import path; critical fixes for existing `lark_oapi.channel`
users are evaluated for backport until 2027-06-02.

`lark-channel-sdk` can be installed alongside `lark-oapi`. Its
[`SecurityConfig`](https://github.com/larksuite/channel-sdk-python/blob/main/docs/security.md)
defaults to compatibility mode so migrated bots can roll out with audit mode
before strict enforcement. See the
[migration guide](https://github.com/larksuite/channel-sdk-python/blob/main/docs/migration-from-lark-oapi.md)
for the full checklist.

```bash
pip install lark-channel-sdk
```

```python
from lark_channel import FeishuChannel
```

Existing legacy import example:

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

Channel documentation:

- [Legacy Channel module](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel.md)
- [Legacy Channel quickstart](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/quickstart.md)
- [Legacy Channel reference](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/doc/channel/reference.md)
- [Standalone Channel migration guide](https://github.com/larksuite/channel-sdk-python/blob/main/docs/migration-from-lark-oapi.md)
- [Standalone Channel security guide](https://github.com/larksuite/channel-sdk-python/blob/main/docs/security.md)
- [Runnable legacy echo bot sample](https://github.com/larksuite/oapi-sdk-python/blob/HEAD/samples/channel/echo_bot.py)

## Examples

More composite API examples and business scenario samples are available in
[oapi-sdk-python-demo](https://github.com/larksuite/oapi-sdk-python-demo).

- [Send file message](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/im/send_file.py)
- [Send image message](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/im/send_image.py)
- [List users under a department](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/contact/list_user_by_department.py)
- [Create a Base app with tables](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/base/create_app_and_tables.py)
- [Robot quick start](https://github.com/larksuite/oapi-sdk-python-demo/blob/main/quick_start/robot)

## License

MIT

## Contact Us

Click [Server SDK](https://open.feishu.cn/document/ukTMukTMukTM/uETO1YjLxkTN24SM5UjN)
in the upper right corner of the documentation page and submit feedback.
