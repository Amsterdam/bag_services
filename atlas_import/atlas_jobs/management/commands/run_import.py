from django.core.management import BaseCommand

from batch import batch
from atlas_jobs import jobs


class Command(BaseCommand):
    def handle(self, *args, **options):
        batch.execute(jobs.ImportJob())
