from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.autonomous_key: AutonomousKey = AutonomousKey(config)
        self.autonomous_key_deletion_plan: AutonomousKeyDeletionPlan = (
            AutonomousKeyDeletionPlan(config)
        )
        self.autonomous_key_recover: AutonomousKeyRecover = AutonomousKeyRecover(config)
        self.key_import_material: KeyImportMaterial = KeyImportMaterial(config)
