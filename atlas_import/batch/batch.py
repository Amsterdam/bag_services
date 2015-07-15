import logging
from django.utils import timezone
from batch.models import JobExecution, TaskExecution

log = logging.getLogger(__name__)


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