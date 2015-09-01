import logging
import sys

from django.utils import timezone

from batch.models import JobExecution, TaskExecution

log = logging.getLogger(__name__)


def execute(job):
    log.info("Creating job: %s", job.name)
    job_execution = JobExecution.objects.create(name=job.name)

    for t in job.tasks():
        # noinspection PyBroadException
        try:
            _execute_task(job_execution, t)
        except:
            log.exception("Job failed: %s", job.name)
            job_execution.date_finished = timezone.now()
            job_execution.status = JobExecution.STATUS_FAILED
            job_execution.save()
            return job_execution

    log.info("Job completed: %s", job.name)
    job_execution.date_finished = timezone.now()
    job_execution.status = JobExecution.STATUS_FINISHED
    job_execution.save()

    return job_execution


def _execute_task(job_execution, task):
    if callable(task):
        task_name = task.__name__
        execute_func = task
        tear_down = None
    else:
        task_name = getattr(task, "name", "no name specified")
        execute_func = task.execute
        tear_down = getattr(task, "tear_down", None)

    log.info("Executing task: %s", task_name)
    task_execution = TaskExecution.objects.create(job=job_execution, name=task_name, date_started=timezone.now())

    try:
        try:
            execute_func()
        finally:
            if tear_down:
                tear_down()
    except:
        e = sys.exc_info()[0]
        log.exception("Task failed: %s", task_name)
        task_execution.date_finished = timezone.now()
        task_execution.status = TaskExecution.STATUS_FAILED
        task_execution.save()
        raise e

    log.info("Task completed: %s", task_name)
    task_execution.date_finished = timezone.now()
    task_execution.status = TaskExecution.STATUS_FINISHED
    task_execution.save()
