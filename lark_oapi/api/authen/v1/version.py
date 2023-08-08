from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.access_token: AccessToken = AccessToken(config)
        self.refresh_access_token: RefreshAccessToken = RefreshAccessToken(config)
        self.user_info: UserInfo = UserInfo(config)
