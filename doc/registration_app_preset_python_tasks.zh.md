# Python 一键创建应用 app_preset 实现任务点

## 背景

Node SDK commit `984bb8d80aa98c5d873ec094287330a377689161` 为 `registerApp` 新增了 `appPreset`，用于在扫码创建应用页面预填应用头像、名称和描述。Python SDK 需要实现同等能力，但使用 Python 风格参数名 `app_preset`。

该能力只影响二维码 URL，不影响 `/oauth/v1/app/registration` 的 `begin` / `poll` 请求体。SDK 接收原始参数值，由 SDK 负责 URL Encode；Web 创建页负责展示、`{user}` 替换、图片处理、用户编辑以及最终提交。

## 设计原则

- 对齐 Node 行为，Python API 使用 snake_case。
- `app_preset` 是创建页初始化预填值，不是最终创建结果的强约束。
- 用户传原始值，例如 `{user}的应用`，不要要求用户预先 URL Encode。
- 保留已有二维码参数：`from=sdk`、`tp=sdk`、`source=python-sdk[/source]`。
- 只做 SDK 侧轻量校验，不探测图片 URL、不校验图片格式、不校验名称和描述长度。

## 公开 API

同步接口新增参数：

```python
def register_app(
    on_qr_code,
    on_status_change=None,
    source=None,
    cancel_event=None,
    domain="https://accounts.feishu.cn",
    lark_domain="https://accounts.larksuite.com",
    app_preset=None,
):
```

异步接口新增参数：

```python
async def aregister_app(
    on_qr_code,
    on_status_change=None,
    source=None,
    domain="https://accounts.feishu.cn",
    lark_domain="https://accounts.larksuite.com",
    app_preset=None,
):
```

`app_preset` 使用 dict：

```python
{
    "avatar": "https://example.com/a.png",
    "name": "{user}的应用",
    "desc": "由业务平台自动生成",
}
```

多个头像：

```python
{
    "avatar": [
        "https://example.com/a.png",
        "https://example.com/b.webp",
        "https://example.com/c.gif",
    ],
}
```

## 任务 1：扩展 flow 构造参数

修改文件：`lark_oapi/scene/registration/__init__.py`

- `_RegistrationFlow.__init__` 新增 `app_preset=None` 参数。
- 保存为 `self._app_preset`。
- `_SyncFlow.__init__` 接收并透传 `app_preset`。
- `_AsyncFlow` 继续复用 `_RegistrationFlow.__init__`。
- `register_app` 创建 `_SyncFlow` 时传入 `app_preset`。
- `aregister_app` 创建 `_AsyncFlow` 时传入 `app_preset`。

建议结构：

```python
class _RegistrationFlow:
    def __init__(self, on_qr_code, on_status_change, source, domain, lark_domain, app_preset=None):
        self._on_qr_code = on_qr_code
        self._on_status_change = on_status_change
        self._source = source
        self._base_url = domain
        self._lark_url = lark_domain
        self._app_preset = app_preset
```

## 任务 2：新增 app_preset URL 参数追加逻辑

修改文件：`lark_oapi/scene/registration/__init__.py`

新增常量：

```python
_AVATAR_MAX_COUNT = 6
```

新增私有方法：

```python
def _apply_app_preset(self, params):
    if not self._app_preset:
        return

    avatar = self._app_preset.get("avatar")
    name = self._app_preset.get("name")
    desc = self._app_preset.get("desc")

    if avatar is not None:
        avatars = avatar if isinstance(avatar, list) else [avatar]
        if len(avatars) == 0:
            raise ValueError("app_preset.avatar must contain at least 1 URL")
        if len(avatars) > _AVATAR_MAX_COUNT:
            raise ValueError(
                f"app_preset.avatar supports at most {_AVATAR_MAX_COUNT} URLs, got {len(avatars)}"
            )
        for index, url in enumerate(avatars):
            if not isinstance(url, str) or url == "":
                raise ValueError(f"app_preset.avatar[{index}] must be a non-empty string")
        params["avatar"] = avatars

    if name is not None:
        params["name"] = name

    if desc is not None:
        params["desc"] = desc
```

如果需要更严格的 Python 运行时类型防御，可以额外校验 `self._app_preset` 必须是 dict、`name` / `desc` 必须是 str。但为了贴近 Node，最小实现只要求 `avatar` 行为一致。

## 任务 3：接入 _build_qr_url

修改文件：`lark_oapi/scene/registration/__init__.py`

在 `_build_qr_url` 设置完已有参数后调用 `_apply_app_preset(params)`：

```python
def _build_qr_url(self, uri):
    parsed = urlparse(uri)
    params = parse_qs(parsed.query)
    params["from"] = "sdk"
    params["tp"] = "sdk"
    params["source"] = f"{_SDK_NAME}/{self._source}" if self._source else _SDK_NAME
    self._apply_app_preset(params)
    return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))
```

保留 `doseq=True`。这是多头像生成重复 query 参数的关键：

```text
avatar=https%3A%2F%2Fexample.com%2Fa.png&avatar=https%3A%2F%2Fexample.com%2Fb.webp
```

## 任务 4：补充代码注释

修改文件：`lark_oapi/scene/registration/__init__.py`

在 `_apply_app_preset` 或 `_build_qr_url` 附近增加简短注释，表达 Node 注释中的关键原因：

```python
# app_preset values are pre-fill values for the app-creation page.
# urlencode handles URL encoding; callers should pass raw values.
```

不要把注释写成“最终应用信息”，因为最终值以用户在 Web 页面提交为准。

## 任务 5：更新 README

修改文件：

- `README.md`
- `README.zh.md`

在一键创建应用参数表增加：

- `app_preset`
- `app_preset.avatar`
- `app_preset.name`
- `app_preset.desc`

英文描述要包含：

- all fields are optional
- users can still edit them on the app-creation page
- SDK handles URL encoding automatically

中文描述要包含：

- 所有字段选填
- 用户扫码后仍可在页面修改
- SDK 自动 URL Encode，调用方传原始值

## 任务 6：补充使用示例

可选修改文件：

- `README.md`
- `README.zh.md`
- 或新增 `samples/registration/app_preset_sample.py`

示例应展示原始值传入：

```python
register_app(
    on_qr_code=lambda info: print(info["url"]),
    app_preset={
        "avatar": [
            "https://example.com/a.png",
            "https://example.com/b.webp",
        ],
        "name": "{user}的应用",
        "desc": "由业务平台自动生成",
    },
)
```

不要在示例中手动调用 `quote` 或预先传 `%7Buser%7D...`。

## 非目标

- 不改 `/oauth/v1/app/registration` 的 begin/poll 请求参数。
- 不上传头像文件。
- 不下载或探测头像 URL。
- 不校验图片格式、跨域、重定向、过期链接。
- 不校验 `name` / `desc` 的中英文长度。
- 不在 SDK 内替换 `{user}`。

