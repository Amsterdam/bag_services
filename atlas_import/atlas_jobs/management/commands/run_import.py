from django.core.management import BaseCommand
import bag.batch

from batch import batch
from atlas_jobs import jobs


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--no-bag',
                            action='store_false',
                            dest='run-bag',
                            default=True,
                            help='Skip BAG import')
        parser.add_argument('--no-kadaster',
                            action='store_false',
                            dest='run-kadaster',
                            default=True,
                            help='Skip kadaster import')
        parser.add_argument('--no-wkpb',
                            action='store_false',
                            dest='run-wkpb',
                            default=True,
                            help='Skip WKPB import')
        parser.add_argument('--no-index',
                            action='store_false',
                            dest='run-index',
                            default=True,
                            help='Skip elastic search indexing')

    def handle(self, *args, **options):
        if options['run-bag']:
            batch.execute(bag.batch.ImportBagJob())

        if options['run-kadaster']:
            batch.execute(jobs.ImportKadasterJob())

        if options['run-wkpb']:
            batch.execute(jobs.ImportWkpbJob())

        if options['run-index']:
            batch.execute(jobs.IndexJob())
