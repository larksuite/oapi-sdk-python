# Python 一键创建应用 app_preset 测试用例

## 单元测试范围

建议新增文件：

- `lark_oapi/scene/registration/tests/test_app_preset.py`

测试重点是二维码 URL 构造。同步和异步流程都复用 `_RegistrationFlow._build_qr_url`，所以大部分用例可直接测试内部 flow，端到端用例再覆盖 `register_app` / `aregister_app` 的参数透传。

## 测试辅助函数

建议在测试文件中定义：

```python
from urllib.parse import parse_qs, urlparse

from lark_oapi.scene.registration import _RegistrationFlow


def build_url(app_preset=None, source=None, raw_url="https://accounts.feishu.cn/page/launcher?ticket=abc"):
    flow = _RegistrationFlow(
        on_qr_code=lambda info: None,
        on_status_change=None,
        source=source,
        domain="https://accounts.feishu.cn",
        lark_domain="https://accounts.larksuite.com",
        app_preset=app_preset,
    )
    return flow._build_qr_url(raw_url)


def parse_query(url):
    return parse_qs(urlparse(url).query)
```

如果不希望测试直接导入私有类，可改为通过 mock `_post` 的方式跑 `register_app`，但直接测 `_build_qr_url` 更聚焦、速度更快。

## 单元测试用例

### 1. 不传 app_preset 时不追加新参数

```python
def test_build_qr_url_omits_app_preset_params_when_not_provided():
    url = build_url()
    query = parse_query(url)

    assert "avatar" not in query
    assert "name" not in query
    assert "desc" not in query
    assert query["from"] == ["sdk"]
    assert query["tp"] == ["sdk"]
    assert query["source"] == ["python-sdk"]
    assert query["ticket"] == ["abc"]
```

### 2. source 不受 app_preset 影响

```python
def test_build_qr_url_keeps_source_with_app_preset():
    url = build_url(app_preset={"name": "X"}, source="lark-cli")
    query = parse_query(url)

    assert query["source"] == ["python-sdk/lark-cli"]
    assert query["name"] == ["X"]
```

### 3. 支持单个头像字符串

```python
def test_build_qr_url_accepts_single_avatar_string():
    url = build_url(app_preset={"avatar": "https://example.com/a.png"})
    query = parse_query(url)

    assert query["avatar"] == ["https://example.com/a.png"]
```

### 4. 支持多个头像且保持顺序

```python
def test_build_qr_url_accepts_avatar_list_and_preserves_order():
    avatars = [
        "https://example.com/a.png",
        "https://example.com/b.webp",
        "https://example.com/c.gif",
    ]

    url = build_url(app_preset={"avatar": avatars})
    query = parse_query(url)

    assert query["avatar"] == avatars
```

### 5. 恰好 6 个头像通过

```python
def test_build_qr_url_accepts_exactly_six_avatars():
    avatars = [f"https://example.com/{index}.png" for index in range(6)]

    url = build_url(app_preset={"avatar": avatars})
    query = parse_query(url)

    assert query["avatar"] == avatars
```

### 6. 超过 6 个头像报错

```python
import pytest


def test_build_qr_url_rejects_more_than_six_avatars():
    avatars = [f"https://example.com/{index}.png" for index in range(7)]

    with pytest.raises(ValueError, match=r"at most 6 URLs, got 7"):
        build_url(app_preset={"avatar": avatars})
```

### 7. 空头像数组报错

```python
def test_build_qr_url_rejects_empty_avatar_list():
    with pytest.raises(ValueError, match=r"at least 1 URL"):
        build_url(app_preset={"avatar": []})
```

### 8. 空头像字符串报错

```python
def test_build_qr_url_rejects_empty_avatar_string():
    with pytest.raises(ValueError, match=r"avatar\[0\].*non-empty string"):
        build_url(app_preset={"avatar": ""})
```

### 9. 头像数组中的空字符串报错且包含索引

```python
def test_build_qr_url_rejects_empty_avatar_list_item_with_index():
    with pytest.raises(ValueError, match=r"avatar\[1\].*non-empty string"):
        build_url(app_preset={"avatar": ["https://example.com/a.png", ""]})
```

### 10. name 支持原始值并由 SDK 编码

```python
def test_build_qr_url_url_encodes_name_with_user_placeholder():
    url = build_url(app_preset={"name": "{user}的应用"})
    query = parse_query(url)

    assert query["name"] == ["{user}的应用"]
    assert "name=%7Buser%7D%E7%9A%84%E5%BA%94%E7%94%A8" in url
```

### 11. desc 支持原始值并由 SDK 编码

```python
def test_build_qr_url_url_encodes_desc():
    url = build_url(app_preset={"desc": "由业务平台自动生成"})
    query = parse_query(url)

    assert query["desc"] == ["由业务平台自动生成"]
    assert "%E7%94%B1%E4%B8%9A%E5%8A%A1%E5%B9%B3%E5%8F%B0" in url
```

### 12. avatar、name、desc 可同时存在

```python
def test_build_qr_url_emits_all_app_preset_fields():
    url = build_url(
        app_preset={
            "avatar": ["https://example.com/a.png", "https://example.com/b.png"],
            "name": "MyApp",
            "desc": "demo",
        }
    )
    query = parse_query(url)

    assert query["avatar"] == ["https://example.com/a.png", "https://example.com/b.png"]
    assert query["name"] == ["MyApp"]
    assert query["desc"] == ["demo"]
```

## 同步端到端测试用例

目标：验证 `register_app(..., app_preset=...)` 能把参数透传到二维码回调。

建议使用 monkeypatch 替换 `_SyncFlow._post` 和 `time.sleep`，避免真实网络和等待。

```python
import time
from urllib.parse import parse_qs, urlparse

import pytest

from lark_oapi.scene import registration


def test_register_app_sync_passes_app_preset_to_qr_url(monkeypatch):
    responses = [
        {"supported_auth_methods": ["client_secret"]},
        {
            "device_code": "dev-1",
            "verification_uri_complete": "https://accounts.feishu.cn/page/launcher",
            "interval": 1,
            "expires_in": 60,
        },
        {
            "client_id": "cli_a",
            "client_secret": "sec_a",
            "user_info": {"open_id": "ou_x", "tenant_brand": "feishu"},
        },
    ]

    def fake_post(self, data):
        return responses.pop(0)

    monkeypatch.setattr(registration._SyncFlow, "_post", fake_post)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    captured = {}

    result = registration.register_app(
        on_qr_code=lambda info: captured.update(info),
        app_preset={
            "avatar": ["https://example.com/a.png", "https://example.com/b.webp"],
            "name": "{user}的应用",
            "desc": "由业务平台自动生成",
        },
    )

    query = parse_qs(urlparse(captured["url"]).query)
    assert query["avatar"] == ["https://example.com/a.png", "https://example.com/b.webp"]
    assert query["name"] == ["{user}的应用"]
    assert query["desc"] == ["由业务平台自动生成"]
    assert result["client_id"] == "cli_a"
    assert result["client_secret"] == "sec_a"
```

## 异步端到端测试用例

目标：验证 `aregister_app(..., app_preset=...)` 与同步接口行为一致。

```python
from urllib.parse import parse_qs, urlparse

import pytest

from lark_oapi.scene import registration


@pytest.mark.asyncio
async def test_register_app_async_passes_app_preset_to_qr_url(monkeypatch):
    responses = [
        {"supported_auth_methods": ["client_secret"]},
        {
            "device_code": "dev-1",
            "verification_uri_complete": "https://accounts.feishu.cn/page/launcher",
            "interval": 1,
            "expires_in": 60,
        },
        {
            "client_id": "cli_a",
            "client_secret": "sec_a",
            "user_info": {"open_id": "ou_x", "tenant_brand": "feishu"},
        },
    ]

    async def fake_post(self, data):
        return responses.pop(0)

    async def fake_sleep(seconds):
        return None

    monkeypatch.setattr(registration._AsyncFlow, "_post", fake_post)
    monkeypatch.setattr(registration.asyncio, "sleep", fake_sleep)

    captured = {}

    result = await registration.aregister_app(
        on_qr_code=lambda info: captured.update(info),
        app_preset={
            "avatar": "https://example.com/a.png",
            "name": "{user}的应用",
            "desc": "由业务平台自动生成",
        },
    )

    query = parse_qs(urlparse(captured["url"]).query)
    assert query["avatar"] == ["https://example.com/a.png"]
    assert query["name"] == ["{user}的应用"]
    assert query["desc"] == ["由业务平台自动生成"]
    assert result["client_id"] == "cli_a"
    assert result["client_secret"] == "sec_a"
```

## 真实环境端到端验证

真实环境 E2E 不建议默认进入 CI，因为需要扫码人工确认。建议作为手动样例或 gated 测试。

步骤：

1. 调用 `register_app`，传入 `app_preset`。
2. 在 `on_qr_code` 中打印 URL 或生成二维码。
3. 打开 URL，确认创建页中头像候选、名称、描述已预填。
4. 确认用户仍可修改这些字段。
5. 提交创建，确认 SDK 返回 `client_id` 和 `client_secret`。

手动脚本示例：

```python
import lark_oapi as lark


def on_qr_code(info):
    print("Open this URL or render it as QR code:")
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

验收点：

- URL 中包含 `avatar`、`name`、`desc`。
- URL 中 `{user}` 被百分号编码，页面展示时由 Web 端替换。
- 多头像按传入顺序展示，第一个默认选中。
- Web 页面允许用户修改预填值。
- 创建成功后返回应用凭证。

