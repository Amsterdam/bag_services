from django.core.management import BaseCommand
from ... import models, jobs


class Command(BaseCommand):

    def handle(self, *args, **options):
        models.execute(jobs.ImportJob())

