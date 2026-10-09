from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.file: File = File(config)
        self.session: Session = Session(config)
        self.session_event: SessionEvent = SessionEvent(config)
        self.session_message: SessionMessage = SessionMessage(config)
