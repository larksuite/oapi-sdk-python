from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.password: Password = Password(config)
        self.session: Session = Session(config)
