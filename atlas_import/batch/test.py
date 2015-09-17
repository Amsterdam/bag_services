from django.test import TestCase
from datasets.generic import cache


class TaskTestCase(TestCase):

    def setUp(self):
        self.cache = cache.Cache()

    def requires(self):
        return []

    def task(self):
        raise NotImplementedError()

    def test_task_attributes(self):
        try:
            t = self.task()
        except NotImplementedError:
            return

        if not hasattr(t, "name"):
            self.fail("No 'name' attribute for {}".format(type(t)))

        if not hasattr(t, "execute") or not callable(t.execute):
            self.fail("No 'execute' method for {}".format(type(t)))

    def run_task(self):
        for r in self.requires():
            r.execute()

        self.task().execute()
        self.cache.flush()