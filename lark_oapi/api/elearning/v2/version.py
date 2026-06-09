from .resource import *


class V2(object):
    def __init__(self, config: Config) -> None:
        self.course_registration: CourseRegistration = CourseRegistration(config)
