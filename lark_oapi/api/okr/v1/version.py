from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.image: Image = Image(config)
        self.metric_source: MetricSource = MetricSource(config)
        self.metric_source_table: MetricSourceTable = MetricSourceTable(config)
        self.metric_source_table_item: MetricSourceTableItem = MetricSourceTableItem(config)
        self.okr: Okr = Okr(config)
        self.period: Period = Period(config)
        self.progress_record: ProgressRecord = ProgressRecord(config)
        self.user_okr: UserOkr = UserOkr(config)
