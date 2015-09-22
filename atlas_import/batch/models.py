from django.db import models
from django.utils import timezone


def _duration(date_started, date_finished=None):
    if not date_started:
        return ""

    if not date_finished:
        date_finished = timezone.now()

    total_seconds = int((date_finished - date_started).total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if not hours and not minutes:
        return "{}s".format(seconds)

    if not hours:
        return "{}m {}s".format(minutes, seconds)

    return "{}h {}m {}s".format(hours, minutes, seconds)


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
        return _duration(self.date_started, self.date_finished)


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
        ordering = ("date_started",)

    def duration(self):
        return _duration(self.date_started, self.date_finished)
