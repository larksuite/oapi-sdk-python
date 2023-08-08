from .resource import *


class V2(object):
    def __init__(self, config: Config) -> None:
        self.comment: Comment = Comment(config)
        self.section: Section = Section(config)
        self.task: Task = Task(config)
        self.task_subtask: TaskSubtask = TaskSubtask(config)
        self.tasklist: Tasklist = Tasklist(config)
