from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.multi_geo_entity_tenant: MultiGeoEntityTenant = MultiGeoEntityTenant(config)
        self.openapi_log: OpenapiLog = OpenapiLog(config)
        self.user_migration: UserMigration = UserMigration(config)
