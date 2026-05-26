import os

from lark_oapi.core.client_assertion import ClientAssertionToken
from lark_oapi.ws import Client


class EnvClientAssertionProvider:
    def retrieve_token(self, aud: str) -> ClientAssertionToken:
        return ClientAssertionToken(os.environ["LARK_CLIENT_ASSERTION"])


client = Client(
    os.environ["LARK_APP_ID"],
    "",
    client_assertion_provider=EnvClientAssertionProvider(),
)

client.start()
