from django.db import models
from django.utils import timezone


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

    def duration(self):
        if not self.date_started:
            return None

        f = self.date_finished or timezone.now()

        return int((f - self.date_started).total_seconds())


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

    def duration(self):
        if not self.date_started:
            return None

        f = self.date_finished or timezone.now()

        return int((f - self.date_started).total_seconds())


