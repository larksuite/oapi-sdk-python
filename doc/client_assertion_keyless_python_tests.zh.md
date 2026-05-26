# Python ClientAssertion 无密钥测试清单

> 后续 AGENT 执行时，请逐项完成并把 `- [ ]` 改成 `- [x]`，或在条目后追加完成标记。本文件只描述测试与 E2E，任务实现见 `doc/client_assertion_keyless_python_tasks.zh.md`。

## 测试文件规划

| 文件 | 覆盖内容 |
| --- | --- |
| `lark_oapi/core/tests/test_client_assertion_core.py` | provider 类型、错误码、OAuth aud/base URL、proxy URL |
| `lark_oapi/core/tests/test_client_assertion_auth.py` | token type 选择、app-only 拒绝、ISV 拒绝、manual user token 优先 |
| `lark_oapi/core/tests/test_client_assertion_token_manager.py` | tenant token OAuth exchange、缓存、provider 错误、空 token、OAuth 错误响应 |
| `lark_oapi/core/tests/test_client_assertion_access_token.py` | authorization code、refresh token、app_secret fallback、OAuth error、TargetInfo proxy |
| `lark_oapi/ws/tests/test_client_assertion.py` | WS bootstrap provider、proxy、headers、空 token、provider error 原样抛出 |
| `lark_oapi/core/tests/test_transport_absolute_url.py` | absolute URL 拼接与相对 URL 兼容 |
| `lark_oapi/core/tests/e2e/test_client_assertion_keyless_local.py` | 本地 mock E2E |
| `lark_oapi/core/tests/e2e/test_client_assertion_keyless_live.py` | 真实环境 smoke E2E，默认跳过 |

## 单元与集成测试用例

### Core / URL 工具

- [x] ✅ `test_resolve_oauth_base_url_default_feishu`
  - 输入：`Config.domain = "https://open.feishu.cn"`
  - 期望：OAuth base URL 为 `https://accounts.feishu.cn`，aud 为 `accounts.feishu.cn`。

- [x] ✅ `test_resolve_oauth_base_url_default_lark`
  - 输入：`Config.domain = "https://open.larksuite.com"`
  - 期望：OAuth base URL 为 `https://accounts.larksuite.com`，aud 为 `accounts.larksuite.com`。

- [x] ✅ `test_resolve_oauth_base_url_explicit_localhost`
  - 输入：`Config.oauth_base_url = "http://127.0.0.1:18080"`
  - 期望：OAuth base URL 保留 http scheme，aud 为 `127.0.0.1:18080`。

- [x] ✅ `test_resolve_oauth_base_url_requires_explicit_for_custom_domain`
  - 输入：`Config.domain = "https://open.feishu-boe.cn"`
  - 期望：未配置 `oauth_base_url` 时抛错。

- [x] ✅ `test_build_proxy_url_adds_https_when_scheme_missing`
  - 输入：`TargetInfo(target_service="proxy.example.com", target_prefix="/proxy")` 和 `/oauth/v3/token`
  - 期望：`https://proxy.example.com/proxy/oauth/v3/token`。

### 鉴权选择

- [x] ✅ `test_verify_client_assertion_prefers_tenant_over_app`
  - request token types 为 `{AccessTokenType.APP, AccessTokenType.TENANT}`。
  - provider 存在。
  - 期望：选择 tenant，`option.tenant_access_token` 被写入。

- [x] ✅ `test_verify_client_assertion_manual_user_token_wins`
  - request token types 为 `{AccessTokenType.TENANT, AccessTokenType.USER}`。
  - 传入 `option.user_access_token`。
  - 期望：不调用 provider，不请求 OAuth token endpoint。

- [x] ✅ `test_verify_client_assertion_rejects_app_only`
  - request token types 为 `{AccessTokenType.APP}`。
  - provider 存在。
  - 期望：返回 `7103`。

- [x] ✅ `test_verify_client_assertion_rejects_isv`
  - `config.app_type = AppType.ISV`。
  - provider 存在。
  - 期望：返回 `7100`。

- [x] ✅ `test_verify_app_secret_mode_still_requires_app_secret`
  - provider 不存在，`app_secret` 为空。
  - 期望：保持现有 `NoAuthorizationException("app_id or app_secret not found")` 行为。

### Tenant token manager

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_requests_oauth_token`
  - fake server 校验 `/oauth/v3/token` body。
  - 期望：body 包含 JWT bearer grant type、client assertion、client id；返回 tenant token 并写缓存。

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_cache_hit_skips_provider`
  - 第一次请求写入缓存，第二次请求同一 app。
  - 期望：第二次不调用 provider。

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_without_cache_miss_calls_provider`
  - 清空 cache 后请求两次。
  - 期望：每次 cache miss 都调用 provider。

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_with_proxy`
  - provider 返回 `TargetInfo(target_service=proxy, target_prefix="/proxy")`。
  - 期望：fake proxy 收到 `/proxy/oauth/v3/token` 和 `X-Target-Service: accounts.feishu.cn`。

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_empty_token`
  - provider 返回 `None` 或 `ClientAssertionToken(value="")`。
  - 期望：返回 `7101`。

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_provider_error`
  - provider 抛 `RuntimeError("boom")`。
  - 期望：返回 `7102`，message 包含 `boom`。

- [x] ✅ `test_get_self_tenant_token_by_client_assertion_oauth_error_message_priority`
  - OAuth 响应无 `access_token`，包含 `error_description` 和 `error`。
  - 期望：错误 message 优先使用 `error_description`。

- [x] ✅ `test_get_self_app_token_blocked_in_client_assertion_mode`
  - provider 存在时调用 `TokenManager.get_self_app_token(config)`。
  - 期望：返回 `7100`。

### Transport

- [x] ✅ `test_build_url_keeps_absolute_http_url`
  - 输入：`uri = "http://127.0.0.1:18080/oauth/v3/token"`。
  - 期望：不拼接 `conf.domain`。

- [x] ✅ `test_build_url_keeps_absolute_https_url`
  - 输入：`uri = "https://accounts.feishu.cn/oauth/v3/token"`。
  - 期望：不拼接 `conf.domain`。

- [x] ✅ `test_build_url_relative_path_unchanged`
  - 输入：`domain = "https://open.feishu.cn"`、`uri = "/open-apis/mock/v1/ping"`。
  - 期望：输出 `https://open.feishu.cn/open-apis/mock/v1/ping`。

### OAuth user AccessToken

- [x] ✅ `test_access_token_authorization_code_with_client_assertion`
  - 调用 `client.access_token.retrieve_by_authorization_code(code="code", redirect_uri="https://example.com/cb", code_verifier="verifier")`。
  - 期望：body 包含 `grant_type=authorization_code`、`client_assertion_type`、`client_assertion`、`client_id`、`code`、`redirect_uri`、`code_verifier`。

- [x] ✅ `test_access_token_refresh_with_client_assertion`
  - 调用 `client.access_token.refresh(refresh_token="refresh-token")`。
  - 期望：body 包含 `grant_type=refresh_token`、`refresh_token` 和 client assertion 字段。

- [x] ✅ `test_access_token_authorization_code_with_app_secret_fallback`
  - provider 为空，`app_secret` 存在。
  - 期望：body 包含 `client_secret`，不包含 client assertion 字段。

- [x] ✅ `test_access_token_refresh_with_app_secret_fallback`
  - provider 为空，`app_secret` 存在。
  - 期望：body 包含 `client_secret` 和 `refresh_token`。

- [x] ✅ `test_access_token_rejects_missing_credentials`
  - provider 和 `app_secret` 都为空。
  - 期望：返回 `7104`。

- [x] ✅ `test_access_token_returns_access_token_exception_for_non_200`
  - OAuth endpoint 返回 HTTP 401，body 包含 `code`、`error`、`error_description`。
  - 期望：抛 `AccessTokenException`，保留所有字段。

- [x] ✅ `test_access_token_proxy_keeps_custom_headers`
  - provider 返回 `TargetInfo`，调用时传自定义 headers。
  - 期望：proxy 收到自定义 header 和 SDK 注入的 `X-Target-Service`。

### WebSocket

- [x] ✅ `test_ws_get_conn_url_with_app_secret_keeps_existing_behavior`
  - 使用 `Client("app_id", "app_secret")`。
  - 期望：body 为 `{"AppID": "app_id", "AppSecret": "app_secret"}`。

- [x] ✅ `test_ws_get_conn_url_with_client_assertion`
  - 使用 `Client("app_id", "", client_assertion_provider=provider)`。
  - 期望：body 为 `{"AppID": "app_id", "ClientAssertion": "assertion"}`，不包含 `AppSecret`。

- [x] ✅ `test_ws_get_conn_url_with_client_assertion_proxy`
  - provider 返回 `TargetInfo`。
  - 期望：请求 URL 为 proxy URL，header `X-Target-Service` 为 WS domain host。

- [x] ✅ `test_ws_get_conn_url_retrieves_token_each_time`
  - provider 依次返回 `assertion-1`、`assertion-2`。
  - 期望：连续两次 `_get_conn_url()` 分别发送两个 assertion。

- [x] ✅ `test_ws_get_conn_url_empty_client_assertion_token`
  - provider 返回空 token。
  - 期望：抛 `ClientException`，code 为 `7101`。

- [x] ✅ `test_ws_provider_error_is_not_wrapped`
  - provider 抛出 `RuntimeError("boom")`。
  - 期望：`_get_conn_url()` 抛出的就是原始 `RuntimeError`。

- [x] ✅ `test_ws_non_200_uses_server_msg_when_available`
  - bootstrap 返回 HTTP 500，body 为 `{"code":20050,"msg":"target service unavailable"}`。
  - 期望：抛 `ServerException(500, "target service unavailable")`。

## 本地 mock E2E

文件：`lark_oapi/core/tests/e2e/test_client_assertion_keyless_local.py`

目标：
- [x] ✅ 覆盖 `provider -> OAuth token exchange -> 普通 OpenAPI 请求带 tenant token` 的完整链路。
- [x] ✅ 覆盖 `client.access_token` authorization code / refresh token 的完整链路。
- [x] ✅ 覆盖 WS bootstrap 的 provider、TargetInfo、headers 链路。

本地 server 需要提供：
- [x] ✅ `POST /oauth/v3/token`：校验 request body，返回 `{"access_token":"tenant-token","expires_in":7200}` 或用户 token 响应。
- [x] ✅ `GET /open-apis/mock/v1/ping`：校验 `Authorization: Bearer tenant-token`，返回 `{"code":0,"msg":"ok"}`。
- [x] ✅ `POST /callback/ws/endpoint`：校验 `ClientAssertion` body，返回 WS endpoint JSON。

本地 E2E 关键断言：
- [x] ✅ provider 收到的 OAuth aud 是 `127.0.0.1:<port>`。
- [x] ✅ OAuth exchange body 使用 JWT bearer grant type。
- [x] ✅ 普通 OpenAPI 请求最终带 tenant token。
- [x] ✅ 第二次普通请求命中 tenant token cache，不再次调用 provider。
- [x] ✅ WS bootstrap 使用 domain host 作为 aud，且 body 不含 `AppSecret`。

推荐命令：

```bash
python -m pytest lark_oapi/core/tests/e2e/test_client_assertion_keyless_local.py -v
```

## 真实环境 E2E

文件：`lark_oapi/core/tests/e2e/test_client_assertion_keyless_live.py`

状态：真实环境 smoke 用例已实现；本机未设置 `LARK_CLIENT_ASSERTION_E2E=1` 和真实凭证，完整回归中按设计跳过。

默认跳过条件：
- [x] ✅ 未设置 `LARK_CLIENT_ASSERTION_E2E=1` 时跳过。
- [x] ✅ 缺少必要环境变量时跳过。

环境变量：
- `LARK_APP_ID`：应用 app id。
- `LARK_CLIENT_ASSERTION`：外部系统已签发好的 assertion。SDK 测试只消费它，不生成它。
- `LARK_OPENAPI_DOMAIN`：可选，默认 `https://open.feishu.cn`。
- `LARK_OAUTH_BASE_URL`：自定义域或 BOE 环境必填，默认按 domain 映射。
- `LARK_OAUTH_CODE`：可选，一次性 authorization code，用于 user token authorization code E2E。
- `LARK_REFRESH_TOKEN`：可选，用于 refresh token E2E。

真实 E2E 分组：
- [x] ✅ tenant token exchange smoke：provider 从 `LARK_CLIENT_ASSERTION` 返回 assertion，断言拿到非空 tenant token。
- [x] ✅ authorization code exchange smoke：仅当 `LARK_OAUTH_CODE` 存在时运行，断言 `access_token` 非空。
- [x] ✅ refresh token smoke：仅当 `LARK_REFRESH_TOKEN` 存在时运行，断言 `access_token` 非空。
- [x] ✅ WS bootstrap smoke：仅当 `LARK_WS_CLIENT_ASSERTION_E2E=1` 存在时运行，只调用 `_get_conn_url()`，不进入长期 `start()` 阻塞循环。

推荐命令：

```bash
LARK_CLIENT_ASSERTION_E2E=1 \
LARK_APP_ID=cli_example \
LARK_CLIENT_ASSERTION=example_assertion \
python -m pytest lark_oapi/core/tests/e2e/test_client_assertion_keyless_live.py -v
```

## 回归命令

新增测试定向运行：

```bash
python -m pytest \
  lark_oapi/core/tests/test_client_assertion_core.py \
  lark_oapi/core/tests/test_client_assertion_auth.py \
  lark_oapi/core/tests/test_client_assertion_token_manager.py \
  lark_oapi/core/tests/test_client_assertion_access_token.py \
  lark_oapi/core/tests/test_transport_absolute_url.py \
  lark_oapi/ws/tests/test_client_assertion.py -v
```

完整回归：

```bash
python -m pytest lark_oapi/core/tests lark_oapi/ws/tests lark_oapi/channel/tests -v
```

## 验收清单

- [x] ✅ app_secret 模式现有测试全部通过。
- [x] ✅ provider 模式允许 app_secret 为空。
- [x] ✅ SDK 不生成、不解析、不签名 JWT。
- [x] ✅ tenant token OAuth exchange 请求体与 GO SDK 一致。
- [x] ✅ OAuth audience 与 WS audience 规则分别正确。
- [x] ✅ TargetInfo proxy URL 和 `X-Target-Service` 与 GO SDK 一致。
- [x] ✅ app-only API 在 provider 模式下返回 `7103`。
- [x] ✅ ISV 应用在 provider 模式下返回 `7100`。
- [x] ✅ WS provider error 原样抛出，空 token 返回 `7101`。
- [x] ✅ 本地 mock E2E 覆盖 OpenAPI、AccessToken、WS 三条链路。
- [x] ✅ 真实环境 E2E 默认跳过，只有显式环境变量开启时才运行。
