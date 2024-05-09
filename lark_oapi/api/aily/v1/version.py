from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.aily_session: AilySession = AilySession(config)
        self.aily_session_aily_message: AilySessionAilyMessage = AilySessionAilyMessage(config)
        self.aily_session_run: AilySessionRun = AilySessionRun(config)
