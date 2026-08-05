from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.connection: Connection = Connection(config)
        self.outbound_ip: OutboundIp = OutboundIp(config)
