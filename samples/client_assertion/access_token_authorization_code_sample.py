import os

import lark_oapi as lark
from lark_oapi.core.client_assertion import ClientAssertionToken


class EnvClientAssertionProvider:
    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        return ClientAssertionToken(os.environ["LARK_CLIENT_ASSERTION"])


builder = (
    lark.Client.builder()
    .app_id(os.environ["LARK_APP_ID"])
    .client_assertion_provider(EnvClientAssertionProvider())
)
if os.environ.get("LARK_OAUTH_BASE_URL"):
    builder.oauth_base_url(os.environ["LARK_OAUTH_BASE_URL"])

client = builder.build()
resp = client.access_token.retrieve_by_authorization_code(
    code=os.environ["LARK_OAUTH_CODE"],
    redirect_uri=os.environ.get("LARK_REDIRECT_URI"),
    code_verifier=os.environ.get("LARK_CODE_VERIFIER"),
)

print("access_token received:", bool(resp.access_token))
print("expires_in:", resp.expires_in)
