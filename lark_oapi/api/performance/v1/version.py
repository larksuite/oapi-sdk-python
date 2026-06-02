from .resource import *


class V1(object):
    def __init__(self, config: Config) -> None:
        self.review_data: ReviewData = ReviewData(config)
        self.semester: Semester = Semester(config)
        self.stage_task: StageTask = StageTask(config)
