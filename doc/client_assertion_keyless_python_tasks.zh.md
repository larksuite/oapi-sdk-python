# Python ClientAssertion 无密钥改造任务清单

> 后续 AGENT 执行时，请逐项完成并把 `- [ ]` 改成 `- [x]`，或在条目后追加完成标记。实现以 `oapi-sdk-go` 当前 `v3_main` 的 ClientAssertion 行为为准，GO 文档仅作辅助。

## 目标

为 Python SDK 增加 ClientAssertion 无密钥模式：调用方注入 `ClientAssertionProvider`，SDK 在需要应用侧凭证时向 provider 获取 `client_assertion`，再向 OAuth 服务换取 tenant access token 或用户 access token。SDK 不生成 JWT、不签名、不保存私钥。

## 当前 Python SDK 现状

| 模块 | 当前职责 | 改造关注点 |
| --- | --- | --- |
| `lark_oapi/client.py` | `ClientBuilder`、全局 `Config`、服务初始化 | 增加 provider、OAuth base URL builder；初始化 `client.access_token` |
| `lark_oapi/core/model/config.py` | 保存 `app_id`、`app_secret`、`domain`、`app_type`、cache 等配置 | 新增 provider 和 OAuth base URL 字段 |
| `lark_oapi/core/token/auth.py` | 请求前鉴权、选择 app/tenant/user token | 加入 ClientAssertion 模式 token type 决策 |
| `lark_oapi/core/token/manager.py` | 获取并缓存 app/tenant token | 增加 OAuth JWT bearer tenant token exchange；ClientAssertion 模式禁止 app token |
| `lark_oapi/core/http/transport.py` | 组装 URL/header/body 并发送 sync/async 请求 | 支持 absolute URL，供 OAuth/proxy endpoint 使用；Debug 日志输出前递归脱敏敏感凭证 |
| `lark_oapi/ws/client.py` | WebSocket endpoint bootstrap 和连接管理 | 支持 provider、TargetInfo 代理、自定义 header 覆盖规则 |

## GO SDK 对齐约束

- [x] ✅ `app_id` 仍然必填；配置 provider 后 `app_secret` 可以为空。
- [x] ✅ `ClientAssertionProvider.retrieve_token(aud)` 每次需要 assertion 时调用；SDK 不缓存 assertion。
- [x] ✅ ClientAssertion 模式只支持自建应用；Python 中对应 `AppType.SELF`。`AppType.ISV` 直接拒绝。
- [x] ✅ 普通 OpenAPI 请求在 ClientAssertion 模式下优先使用 tenant token；显式传入 user token 且接口支持 user token 时继续使用 user token。
- [x] ✅ AppAccessToken-only API 在 ClientAssertion 模式下报 `7103`。
- [x] ✅ tenant token 使用 `POST {oauth_base_url}/oauth/v3/token`，grant type 为 `urn:ietf:params:oauth:grant-type:jwt-bearer`。
- [x] ✅ OAuth audience 使用 OAuth host；WS audience 使用 WS domain host。
- [x] ✅ `TargetInfo` 只做朴素拼接：`target_service + target_prefix + api_path`；`target_service` 无 scheme 时补 `https://`。
- [x] ✅ tenant token 缓存 TTL 按 `expires_in - 3min`；Python 当前 cache 接口接收绝对 Unix 过期时间，因此写入 `time.time() + max(expires_in - 180, 0)`。
- [x] ✅ WS provider 获取失败时直接返回原始错误，不包装成 `7102`；空 token 仍返回 `7101`。

## 建议新增公共类型

文件：`lark_oapi/core/client_assertion.py`

```python
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class TargetInfo:
    target_service: str
    target_prefix: str = ""


@dataclass
class ClientAssertionToken:
    value: str
    target_info: Optional[TargetInfo] = None


class ClientAssertionProvider(Protocol):
    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        raise NotImplementedError
```

## 实现任务点

### 任务 1：常量、错误和 URL 工具

涉及文件：
- `lark_oapi/core/const.py`
- `lark_oapi/core/exception.py`
- `lark_oapi/core/client_assertion.py`
- `lark_oapi/core/__init__.py`

- [x] ✅ 增加 OAuth 域名常量：`FEISHU_OAUTH_DOMAIN = "https://accounts.feishu.cn"`、`LARK_OAUTH_DOMAIN = "https://accounts.larksuite.com"`。
- [x] ✅ 增加 OAuth token path：`OAUTH_TOKEN_URI = "/oauth/v3/token"`。
- [x] ✅ 增加 grant/type 常量：`GRANT_TYPE_JWT_BEARER`、`CLIENT_ASSERTION_TYPE_JWT_BEARER`。
- [x] ✅ 增加 header 常量：`X_TARGET_SERVICE = "X-Target-Service"`。
- [x] ✅ 增加错误码常量：`7100` 到 `7104`，命名对齐 GO SDK。
- [x] ✅ 新增 `TargetInfo`、`ClientAssertionToken`、`ClientAssertionProvider`。
- [x] ✅ 新增 `ClientAssertionException(code, msg)`，用于 provider 为空、token 为空、模式不支持等本地错误。
- [x] ✅ 新增 `AccessTokenException(status_code, code, error, error_description)`，用于 OAuth user token API 非 200 响应。
- [x] ✅ 新增 `extract_aud_from_url(raw_url)`：无 scheme 时补 `https://`，返回 host，支持端口。
- [x] ✅ 新增 `resolve_oauth_base_url(config)`：显式 `config.oauth_base_url` 优先，否则默认 OpenAPI host 映射 accounts host。
- [x] ✅ 新增 `resolve_oauth_aud(config)`：从 OAuth base URL 解析 host。
- [x] ✅ 新增 `build_proxy_url(target_info, api_path)`：无 scheme 时补 `https://`，然后朴素拼接。
- [x] ✅ 在 `lark_oapi/core/__init__.py` 导出新增类型和工具。

验收方框：
- [x] ✅ 默认 Feishu/Lark audience 正确。
- [x] ✅ 自定义 `oauth_base_url="http://127.0.0.1:18080"` 时 aud 为 `127.0.0.1:18080`。
- [x] ✅ 自定义 OpenAPI domain 且未配置 OAuth base URL 时抛出清晰错误。
- [x] ✅ proxy URL 拼接不额外修正斜杠，保持 GO 行为。

### 任务 2：ClientBuilder 和 Config 入口

涉及文件：
- `lark_oapi/core/model/config.py`
- `lark_oapi/client.py`

- [x] ✅ `Config` 增加 `client_assertion_provider` 字段。
- [x] ✅ `Config` 增加 `oauth_base_url` 字段。
- [x] ✅ `ClientBuilder` 增加 `client_assertion_provider(provider)`。
- [x] ✅ `ClientBuilder` 增加 `oauth_base_url(oauth_base_url: str)`。
- [x] ✅ `Client` 增加 `access_token` 属性，命名遵循现有 lowercase service 风格。
- [x] ✅ `ClientBuilder.build()` 初始化 `client.access_token` 服务。
- [x] ✅ provider 和 `app_secret` 同时配置时，OAuth/token/WS 路径优先使用 provider。

验收方框：
- [x] ✅ `Client.builder().app_id("cli_example").client_assertion_provider(provider).build()` 成功。
- [x] ✅ provider 存在时 `app_secret` 为空不会在 build 阶段失败。
- [x] ✅ 未配置 provider 的 app_secret 模式保持现有行为。

### 任务 3：鉴权选择逻辑

涉及文件：
- `lark_oapi/core/token/auth.py`

- [x] ✅ 在 `verify(config, request, option)` 开头加入 ClientAssertion 分支。
- [x] ✅ provider 存在且 `config.app_id` 为空时报清晰错误：`app_id not found`。
- [x] ✅ provider 存在且 `config.app_type == AppType.ISV` 时返回 `7100`。
- [x] ✅ `option.user_access_token` 非空且接口支持 `AccessTokenType.USER` 时选择 user token，并且不调用 provider。
- [x] ✅ 接口支持 `AccessTokenType.TENANT` 时调用 `TokenManager.get_self_tenant_token(config)`。
- [x] ✅ tenant token 获取成功后写入 `option.tenant_access_token`，并将 `request.token_types` 改为 `{AccessTokenType.TENANT}`。
- [x] ✅ 仅支持 `AccessTokenType.APP` 时返回 `7103`。
- [x] ✅ provider 不存在时保持现有 app_secret 模式兼容。

验收方框：
- [x] ✅ tenant+app 混合 token types 在 provider 模式下选择 tenant。
- [x] ✅ 显式 user token 在 provider 模式下不触发 tenant token exchange。
- [x] ✅ app-only API 在 provider 模式下返回 `7103`。
- [x] ✅ ISV + provider 返回 `7100`。

### 任务 4：tenant token 的 ClientAssertion exchange

涉及文件：
- `lark_oapi/core/token/manager.py`
- `lark_oapi/core/token/__init__.py`

- [x] ✅ `TokenManager.get_self_app_token(config)` 在 provider 存在时直接返回 `7100`，信息对齐 GO：ClientAssertion 模式不支持 AppAccessToken。
- [x] ✅ `TokenManager.get_self_tenant_token(config)` 在 provider 存在时先按当前 Python tenant token cache key 读取缓存。
- [x] ✅ cache miss 时解析 OAuth base URL 和 aud。
- [x] ✅ cache miss 时调用 `config.client_assertion_provider.retrieve_token(aud)`。
- [x] ✅ provider 抛错时包装为 `7102`，message 保留原始错误。
- [x] ✅ token 为 `None` 或 `value` 为空时报 `7101`。
- [x] ✅ 请求 `POST {oauth_base_url}/oauth/v3/token`。
- [x] ✅ 请求 body 包含 `grant_type`、`client_assertion_type`、`client_assertion`、`client_id`。
- [x] ✅ `TargetInfo` 存在时改走 proxy URL，并设置 `X-Target-Service` 为真实 OAuth aud。
- [x] ✅ 响应无 `access_token` 时，错误 message 优先 `error_description`，其次 `error`，最后 `oauth token response missing access token`。
- [x] ✅ 成功后缓存 tenant token，过期时间为 `time.time() + max(expires_in - 180, 0)`。
- [x] ✅ cache key 先沿用现有 `self_tenant_token:{app_id}`；如产品明确要求隔离，再加 mode suffix。

验收方框：
- [x] ✅ 请求路径是 `/oauth/v3/token`。
- [x] ✅ 请求体字段和 GO SDK 完全一致。
- [x] ✅ provider 每次 cache miss 被调用；cache hit 不调用 provider。
- [x] ✅ `expires_in < 180` 时不会写入过去时间导致异常。

### 任务 5：Transport 支持 absolute URL

涉及文件：
- `lark_oapi/core/http/transport.py`

- [x] ✅ `_build_url(domain, uri, paths)` 支持 `uri` 为 `http://` 或 `https://` 开头的完整 URL。
- [x] ✅ absolute URL 只替换 path params，不再拼接 `domain`。
- [x] ✅ 相对 URL 仍按现有逻辑拼接 `domain + uri`。
- [x] ✅ OAuth token exchange 调用方直接解析 OAuth 响应，不走 `Client.request()` 的 `BaseResponse` 语义。
- [x] ✅ 保持自定义 headers、User-Agent、Content-Type 行为不回退。
- [x] ✅ Debug 日志在序列化前递归脱敏 `Authorization`、`client_assertion`、`ClientAssertion`、`client_secret`、`AppSecret`、`*token*` 等敏感字段。
- [x] ✅ 脱敏只作用于日志副本，不修改真实请求 headers/body。

验收方框：
- [x] ✅ absolute OAuth URL 不被拼成 `https://open.feishu.cnhttps://accounts.example.com/oauth/v3/token`。
- [x] ✅ 普通 OpenAPI 相对路径行为不变。
- [x] ✅ 同步和异步 Transport Debug 日志均不会输出 ClientAssertion、AppSecret、Authorization bearer token 等原文。

### 任务 6：OAuth user AccessToken 服务

新增文件建议：
- `lark_oapi/core/access_token/__init__.py`
- `lark_oapi/core/access_token/client.py`
- `lark_oapi/core/access_token/model.py`

修改文件：
- `lark_oapi/client.py`

- [x] ✅ 新增 `client.access_token` 服务。
- [x] ✅ 提供 `retrieve_by_authorization_code(code, redirect_uri=None, code_verifier=None, scope=None)`。
- [x] ✅ 提供 `refresh(refresh_token, scope=None)`。
- [x] ✅ provider 存在时 body 使用 `client_assertion_type` 和 `client_assertion`。
- [x] ✅ provider 不存在且 `app_secret` 存在时 body 使用 `client_secret`。
- [x] ✅ provider 和 `app_secret` 都为空时报 `7104`。
- [x] ✅ 成功响应暴露 `access_token`、`token_type`、`expires_in`、`refresh_token`、`refresh_token_expires_in`、`scope`。
- [x] ✅ 非 200 响应抛 `AccessTokenException`，保留 HTTP status code、`code`、`error`、`error_description`。
- [x] ✅ `TargetInfo` 存在时走 proxy URL，并设置 `X-Target-Service` 为真实 OAuth aud。

验收方框：
- [x] ✅ authorization code 与 refresh token 的 body 字段分别正确。
- [x] ✅ app_secret fallback 不包含 client assertion 字段。
- [x] ✅ PKCE 字段 `code_verifier` 透传。
- [x] ✅ OAuth error response 不被当成普通 OpenAPI `{code,msg}`。

### 任务 7：WebSocket ClientAssertion bootstrap

涉及文件：
- `lark_oapi/ws/client.py`
- `lark_oapi/ws/exception.py`

- [x] ✅ `Client.__init__` 增加 `client_assertion_provider=None`。
- [x] ✅ `_get_conn_url()` 中 provider 和 `app_secret` 不能同时都为空。
- [x] ✅ provider 存在时 aud 使用 `_domain` 的 host。
- [x] ✅ provider 抛错时直接抛原始错误，保持 GO 细节。
- [x] ✅ token 为空时报 `ClientException(7101, "client assertion token is empty")`。
- [x] ✅ provider 模式 body 发送 `{"AppID": app_id, "AppSecret": "", "ClientAssertion": token.value}`，保留必填的 `AppSecret` 字段为空串。
- [x] ✅ `TargetInfo` 存在时 URL 改为 proxy URL，并设置 `X-Target-Service` 为真实 aud。
- [x] ✅ 用户 headers 先合并，SDK 注入的 `locale`、`User-Agent`、`X-Target-Service` 后覆盖。
- [x] ✅ 非 200 响应如果 body 可解析出 `msg`，使用服务端 msg；否则使用 `system busy`。
- [x] ✅ 缺少凭证时错误文案说明 `app_id` 必填，且 `app_secret` / `client_assertion_provider` 至少提供一个。

验收方框：
- [x] ✅ app_secret bootstrap 旧行为不变。
- [x] ✅ provider bootstrap 传空串 `AppSecret`，不传真实密钥。
- [x] ✅ 每次 `_get_conn_url()` 都调用 provider。
- [x] ✅ 自定义 header 不丢失，冲突时 `X-Target-Service` 使用 SDK 注入值。

### 任务 8：样例和文档

新增文件建议：
- `samples/client_assertion/client_assertion_provider_sample.py`
- `samples/client_assertion/access_token_authorization_code_sample.py`
- `samples/ws/client_assertion_sample.py`

修改文件：
- `README.md`
- `README.zh.md`

- [x] ✅ 给出最小 provider 样例，从环境变量读取已生成的 assertion。
- [x] ✅ 明确 SDK 不生成 JWT；生产环境建议 provider 对接 KMS、Vault 或内部签发服务。
- [x] ✅ 写清 `oauth_base_url` 何时需要配置。
- [x] ✅ 写清 ISV / app-only API 不支持。
- [x] ✅ README 中 app_secret 模式说明不被破坏。

## 建议实现顺序

- [x] ✅ 先做任务 1 和任务 2，只暴露类型与配置入口。
- [x] ✅ 再做任务 3 到任务 5，让普通 OpenAPI 的 tenant token 链路跑通。
- [x] ✅ 然后做任务 6，补齐 OAuth user AccessToken API。
- [x] ✅ 再做任务 7，补齐 WS。
- [x] ✅ 最后做任务 8，并跑完整回归和本地 mock E2E。
