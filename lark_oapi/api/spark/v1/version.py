from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.app: App = App(config)
        self.app_enum: AppEnum = AppEnum(config)
        self.app_storage: AppStorage = AppStorage(config)
        self.app_table: AppTable = AppTable(config)
        self.app_view: AppView = AppView(config)
        self.directory_user: DirectoryUser = DirectoryUser(config)
