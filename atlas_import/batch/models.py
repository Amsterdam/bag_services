import logging
from django.db import models
from django.utils import timezone


log = logging.getLogger(__name__)


class JobExecution(models.Model):

    STATUS_RUNNING = 0
    STATUS_FINISHED = 1
    STATUS_FAILED = 2

    STATUS_CHOICES = (
        (STATUS_RUNNING, 'Running'),
        (STATUS_FINISHED, 'Finished'),
        (STATUS_FAILED, 'Failed'),
    )

    name = models.CharField(max_length=100)
    date_started = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True)
    status = models.IntegerField(default=STATUS_RUNNING, choices=STATUS_CHOICES)


class TaskExecution(models.Model):

    STATUS_STARTED = 0
    STATUS_FINISHED = 1
    STATUS_FAILED = 2

    STATUS_CHOICES = (
        (STATUS_STARTED, 'Started'),
        (STATUS_FINISHED, 'Finished'),
        (STATUS_FAILED, 'Failed')
    )

    name = models.CharField(max_length=100)
    date_started = models.DateTimeField(null=True)
    date_finished = models.DateTimeField(null=True)
    status = models.IntegerField(default=STATUS_STARTED, choices=STATUS_CHOICES)
    job = models.ForeignKey(JobExecution, related_name="task_executions")


def execute(job):
    log.info("Creating job")
    job_execution = JobExecution.objects.create(name=job.name)

    for t in job.tasks():
        if callable(t):
            task_function = t
            task_name = t.__name__
        else:
            task_function = t.execute
            task_name = getattr(t, "name", "no name specified")

        try:
            _execute_task(job_execution, task_name, task_function)
        except Exception:
            log.exception("Job failed: %s", task_name)
            job_execution.date_finished = timezone.now()
            job_execution.status = JobExecution.STATUS_FAILED
            job_execution.save()
            return job_execution

    log.info("Job completed")
    job_execution.date_finished = timezone.now()
    job_execution.status = JobExecution.STATUS_FINISHED
    job_execution.save()

    return job_execution


def _execute_task(job_execution, task_name, task_function):
    log.info("Executing task %s", task_name)
    task_execution = TaskExecution.objects.create(job=job_execution, name=task_name, date_started=timezone.now())

    try:
        task_function()
    except Exception as e:
        log.exception("Task failed: %s", task_name)
        task_execution.date_finished = timezone.now()
        task_execution.status = TaskExecution.STATUS_FAILED
        task_execution.save()
        raise e

    log.info("Task completed")
    task_execution.date_finished = timezone.now()
    task_execution.status = TaskExecution.STATUS_FINISHED
    task_execution.save()
