from .resource import *


class V4(object):
    def __init__(self, config: Config) -> None:
        self.bot: Bot = Bot(config)
