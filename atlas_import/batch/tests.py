from django.test import TestCase
from . import models
import batch.batch


class EmptyJob(object):

    name = "empty"

    def tasks(self):
        return []


class FailingTask(object):

    name = "failing"

    def execute(self):
        raise Exception("Oops")


class FailedJob(object):

    name = "failed"

    def tasks(self):
        return [FailingTask()]


class SimpleJob(object):

    def __init__(self, name, *tasks):
        self.name = name
        self._tasks = tasks

    def tasks(self):
        return self._tasks


class JobTest(TestCase):

    def test_job_results_in_execution(self):
        e = batch.batch.execute(EmptyJob())

        self.assertIsNotNone(e)
        self.assertIsNotNone(e.date_started)
        self.assertEqual(e.name, "empty")

    def test_successful_job_results_in_successful_execution(self):
        e = batch.batch.execute(EmptyJob())

        self.assertIsNotNone(e.date_finished)
        self.assertEqual(e.status, models.JobExecution.STATUS_FINISHED)

    def test_failed_job_results_in_failed_execution(self):
        e = batch.batch.execute(FailedJob())

        self.assertIsNotNone(e.date_finished)
        self.assertEqual(e.status, models.JobExecution.STATUS_FAILED)

    def test_task_can_be_function(self):
        done = False

        def update_done():
            nonlocal done
            done = True

        e = batch.batch.execute(SimpleJob("simple", update_done))
        self.assertEqual(e.status, models.JobExecution.STATUS_FINISHED)
        self.assertEqual(done, True)

    def test_job_keeps_track_of_task_executions(self):
        def noop():
            pass

        e = batch.batch.execute(SimpleJob("simple", noop, noop))
        self.assertEqual(e.status, models.JobExecution.STATUS_FINISHED)
        self.assertIsNotNone(e.task_executions)

        t = e.task_executions.all()
        self.assertEqual(len(t), 2)
        self.assertEqual(t[0].status, models.TaskExecution.STATUS_FINISHED)
        self.assertEqual(t[1].status, models.TaskExecution.STATUS_FINISHED)

    def test_task_results_in_execution(self):
        class Task(object):

            def __init__(self):
                self.executed = False
                self.torn_down = False

            def execute(self):
                self.executed = True

            def tear_down(self):
                self.torn_down = True

        t = Task()

        batch.batch.execute(SimpleJob("simple", t))
        self.assertEqual(t.executed, True)
        self.assertEqual(t.torn_down, True)


