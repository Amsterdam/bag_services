from django.test import TransactionTestCase


class TaskTestCase(TransactionTestCase):

    def setUp(self):
        for r in self.requires():
            r.execute()

    def requires(self):
        return []

    def task(self):
        raise NotImplementedError()

    def test_run_twice(self):
        if self.__class__ == TaskTestCase:
            # only run this on subclasses
            return

        self.run_task()
        self.run_task()

    def test_task_attributes(self):
        if self.__class__ == TaskTestCase:
            # only run this on subclasses
            return

        t = self.task()

        if not hasattr(t, "name"):
            self.fail("No 'name' attribute for {}".format(type(t)))

        if not hasattr(t, "execute") or not callable(t.execute):
            self.fail("No 'execute' method for {}".format(type(t)))

    def run_task(self):
        self.task().execute()
