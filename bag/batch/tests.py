from django.test import TransactionTestCase

from batch import batch


class EmptyJob(batch.BasicJob):
    name = "empty"

    def tasks(self):
        return []


class FailingTask(object):
    name = "failing"

    def execute(self):
        raise Exception()


class FailedJob(batch.BasicJob):
    name = "failed"

    def tasks(self):
        return [FailingTask()]


class SimpleJob(batch.BasicJob):
    def __init__(self, name, *tasks):
        self.name = name
        self._tasks = tasks

    def tasks(self):
        return self._tasks


class JobTest(TransactionTestCase):

    def test_task_can_be_function(self):
        done = False

        def update_done():
            nonlocal done
            done = True

    def test_task_results_in_execution(self):
        class Task(object):
            def __init__(self):
                self.executed = False
                self.torn_down = False

            def execute(self):
                self.executed = True

        t = Task()

        batch.execute(SimpleJob("simple", t))
        self.assertEqual(t.executed, True)
