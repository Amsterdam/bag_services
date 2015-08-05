from django.core.management import BaseCommand

from batch import batch
from atlas_jobs import jobs


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--no-import',
                            action='store_false',
                            dest='run-import',
                            default=True,
                            help='Skip database import')
        parser.add_argument('--no-index',
                            action='store_false',
                            dest='run-index',
                            default=True,
                            help='Skip elastic search indexing')

    def handle(self, *args, **options):
        if options['run-import']:
            batch.execute(jobs.ImportJob())

        if options['run-index']:
            batch.execute(jobs.IndexJob())
