import os

import lark_oapi as lark
from lark_oapi.core.client_assertion import ClientAssertionToken


class EnvClientAssertionProvider:
    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        # The SDK does not generate or sign JWTs. Fetch the assertion from
        # your signing service, KMS, Vault, or another secure source.
        return ClientAssertionToken(os.environ["LARK_CLIENT_ASSERTION"])


client = (
    lark.Client.builder()
    .app_id(os.environ["LARK_APP_ID"])
    .client_assertion_provider(EnvClientAssertionProvider())
    .build()
)

print(client.config.app_id)
