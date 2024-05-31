from domain.tasks.models.task_payload import TaskPayload


class TestTask(TaskPayload):
    __test__ = False

    value: str
