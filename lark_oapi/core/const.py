# Info
PROJECT = "oapi-sdk-python"
VERSION = "1.7.0"

# Domain
FEISHU_DOMAIN = "https://open.feishu.cn"
LARK_DOMAIN = "https://open.larksuite.com"
FEISHU_OAUTH_DOMAIN = "https://accounts.feishu.cn"
LARK_OAUTH_DOMAIN = "https://accounts.larksuite.com"

# Header
USER_AGENT = "User-Agent"
AUTHORIZATION = "Authorization"
X_TARGET_SERVICE = "X-Target-Service"
X_TT_LOGID = "X-Tt-Logid"
X_REQUEST_ID = "X-Request-Id"
CONTENT_TYPE = "Content-Type"
Content_Disposition = "Content-Disposition"
LARK_REQUEST_TIMESTAMP = "X-Lark-Request-Timestamp"
LARK_REQUEST_NONCE = "X-Lark-Request-Nonce"
LARK_REQUEST_SIGNATURE = "X-Lark-Signature"

# Content-Type
APPLICATION_JSON = "application/json"

# Event
URL_VERIFICATION = "url_verification"

UTF_8 = "UTF-8"

# OAuth / ClientAssertion
OAUTH_TOKEN_URI = "/oauth/v3/token"
GRANT_TYPE_AUTHORIZATION_CODE = "authorization_code"
GRANT_TYPE_REFRESH_TOKEN = "refresh_token"
GRANT_TYPE_JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
CLIENT_ASSERTION_TYPE_JWT_BEARER = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"

# ClientAssertion error codes, aligned with oapi-sdk-go.
ERR_CODE_CLIENT_ASSERTION_PROVIDER_NOT_CONFIGURED = 7100
ERR_CODE_CLIENT_ASSERTION_TOKEN_EMPTY = 7101
ERR_CODE_CLIENT_ASSERTION_RETRIEVE_FAILED = 7102
ERR_CODE_CLIENT_ASSERTION_MODE_NOT_SUPPORTED = 7103
ERR_CODE_APP_SECRET_AND_CLIENT_ASSERTION_EMPTY = 7104
