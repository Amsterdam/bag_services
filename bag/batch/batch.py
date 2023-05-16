from __future__ import annotations

import gc
import logging
from typing import Optional, List

log = logging.getLogger(__name__)


def execute(job: BasicJob, filter: Optional[List[str]] = None):
    log.info("Starting job: %s [%s]", job.name, job.__class__.__name__)

    for task in job.tasks():
        if not filter or getattr(task, "id_", None) in filter:
            _execute_task(task)

    log.info("Finished job: %s: [%s]", job.name, job.__class__.__name__)


def _execute_task(task):

    if callable(task):
        task_name = task.__name__
        execute_func = task
    else:
        task_name = getattr(task, "name", "no name specified")
        execute_func = task.execute

    log.debug("Starting task: %s", task_name)

    execute_func()


class BasicTask:
    """
    Abstract task that splits execution into three parts:

    * ``before``
    * ``process``
    * ``after``

    """
    name = "Basic Task"

    def execute(self):
        self.before()
        self.process()
        self.after()
        gc.collect()

    def before(self):
        pass

    def after(self):
        pass

    def process(self):
        pass


class BasicJob:
    """Interface for jobs"""
    name = None

    def tasks(self) -> list:
        pass
