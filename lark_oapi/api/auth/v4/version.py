from .resource import *


class V4(object):
    def __init__(self, config: Config) -> None:
        self.user_access_token: UserAccessToken = UserAccessToken(config)
