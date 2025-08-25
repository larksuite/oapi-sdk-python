from utils.feishu.message.v4.resource import *


class V4(object):
    def __init__(self, config: Config) -> None:
        self.batch_send: BatchSend = BatchSend(config)
