from .resource import *


class V6(object):
    def __init__(self, config: Config) -> None:
        self.app_recommend_rule: AppRecommendRule = AppRecommendRule(config)
        self.application: Application = Application(config)
        self.application_app_usage: ApplicationAppUsage = ApplicationAppUsage(config)
        self.application_app_version: ApplicationAppVersion = ApplicationAppVersion(config)
        self.application_contacts_range: ApplicationContactsRange = ApplicationContactsRange(config)
        self.application_feedback: ApplicationFeedback = ApplicationFeedback(config)
        self.application_visibility: ApplicationVisibility = ApplicationVisibility(config)
        self.bot: Bot = Bot(config)
