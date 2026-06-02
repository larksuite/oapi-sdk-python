from .resource import *


class V5(object):
    def __init__(self, config: Config) -> None:
        self.application: Application = Application(config)
