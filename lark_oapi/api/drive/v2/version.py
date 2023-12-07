from .resource import *


class V2(object):
    def __init__(self, config: Config) -> None:
        self.permission_public: PermissionPublic = PermissionPublic(config)
