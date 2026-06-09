from .resource import *


class V7(object):
    def __init__(self, config: Config) -> None:
        self.app_avatar_upload: AppAvatarUpload = AppAvatarUpload(config)
        self.application_ability: ApplicationAbility = ApplicationAbility(config)
        self.application_base: ApplicationBase = ApplicationBase(config)
        self.application_config: ApplicationConfig = ApplicationConfig(config)
        self.application_publish: ApplicationPublish = ApplicationPublish(config)
