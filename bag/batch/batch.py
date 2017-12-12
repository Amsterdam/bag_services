from abc import ABCMeta, abstractmethod
import logging

import gc

log = logging.getLogger(__name__)


def execute(job):
    log.info("Starting job: %s", job.name)

    for task in job.tasks():
        _execute_task(task)

    log.info("Finished job: %s", job.name)


def _execute_task(task):

    if callable(task):
        task_name = task.__name__
        execute_func = task
    else:
        task_name = getattr(task, "name", "no name specified")
        execute_func = task.execute

    log.debug("Starting task: %s", task_name)

    execute_func()


class BasicTask(object):
    """
    Abstract task that splits execution into three parts:

    * ``before``
    * ``process``
    * ``after``

    """

    class Meta:
        __class__ = ABCMeta

    def execute(self):
        self.before()
        self.process()
        self.after()
        gc.collect()

    @abstractmethod
    def before(self):
        pass

    @abstractmethod
    def after(self):
        pass

    @abstractmethod
    def process(self):
        pass
