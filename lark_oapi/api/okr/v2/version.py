from .resource import *


class V2(object):
    def __init__(self, config: Config) -> None:
        self.okr_alignment: OkrAlignment = OkrAlignment(config)
        self.okr_category: OkrCategory = OkrCategory(config)
        self.okr_cycle: OkrCycle = OkrCycle(config)
        self.okr_cycle_objective: OkrCycleObjective = OkrCycleObjective(config)
        self.okr_indicator: OkrIndicator = OkrIndicator(config)
        self.okr_key_result: OkrKeyResult = OkrKeyResult(config)
        self.okr_key_result_indicator: OkrKeyResultIndicator = OkrKeyResultIndicator(
            config
        )
        self.okr_key_result_progress: OkrKeyResultProgress = OkrKeyResultProgress(
            config
        )
        self.okr_objective: OkrObjective = OkrObjective(config)
        self.okr_objective_alignment: OkrObjectiveAlignment = OkrObjectiveAlignment(
            config
        )
        self.okr_objective_indicator: OkrObjectiveIndicator = OkrObjectiveIndicator(
            config
        )
        self.okr_objective_key_result: OkrObjectiveKeyResult = OkrObjectiveKeyResult(
            config
        )
        self.okr_objective_progress: OkrObjectiveProgress = OkrObjectiveProgress(config)
