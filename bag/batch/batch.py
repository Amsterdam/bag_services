from abc import ABCMeta, abstractmethod
import logging
import sys

from django.utils import timezone
import gc

from batch.models import JobExecution, TaskExecution

log = logging.getLogger(__name__)


def execute(job):
    log.info("Starting job: %s", job.name)

    job_execution = JobExecution.objects.create(name=job.name)

    for t in job.tasks():
        _execute_task(job_execution, t)

    log.info("Finished job: %s", job.name)
    job_execution.date_finished = timezone.now()
    job_execution.status = JobExecution.STATUS_FINISHED
    job_execution.save()

    return job_execution


def _execute_task(job_execution, task):

    if callable(task):
        task_name = task.__name__
        execute_func = task
    else:
        task_name = getattr(task, "name", "no name specified")
        execute_func = task.execute

    log.debug("Starting task: %s", task_name)
    task_execution = TaskExecution.objects.create(
        job=job_execution, name=task_name, date_started=timezone.now())

    execute_func()

    log.debug("Finished task: %s", task_name)
    task_execution.date_finished = timezone.now()
    task_execution.status = TaskExecution.STATUS_FINISHED
    task_execution.save()


class BasicTask(object):
    """
    Abstract task that splits execution into three parts:

    * ``before``
    * ``process``
    * ``after``

    ``after`` is *always* called, whether ``process`` fails or not
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
