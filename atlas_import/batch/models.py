from django.db import models


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

    class Meta:
        ordering = ("date_started", )
