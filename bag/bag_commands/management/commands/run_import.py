"""
Database import commands
"""

import sys

from django.core.management import BaseCommand

import datasets.bag.batch
import datasets.brk.batch
import datasets.wkpb.batch
from datasets import validate_tables
from batch import batch


class Command(BaseCommand):
    """
    Import datainto database. with options to select dataset
    """
    ordered = ['bag', 'brk', 'wkpb', 'gebieden']

    imports = dict(
        bag=[datasets.bag.batch.ImportBagJob],
        brk=[datasets.brk.batch.ImportKadasterJob],
        wkpb=[datasets.wkpb.batch.ImportWkpbJob],
        gebieden=[],
    )

    indexes = dict(
        bag=[datasets.bag.batch.IndexBagJob],
        brk=[datasets.brk.batch.IndexKadasterJob],
        wkpb=[],
        gebieden=[datasets.bag.batch.IndexGebiedenJob],
    )

    def add_arguments(self, parser):

        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to import, choose from {}".format(
                ', '.join(self.imports.keys())))

        parser.add_argument(
            '--validate',
            action='store_true',
            dest='validate',
            default=False,
            help='Skip database importing')


    def handle(self, *args, **options):
        dataset = options['dataset']

        for one_ds in dataset:
            if one_ds not in self.imports.keys():
                self.stderr.write("Unkown dataset: {}".format(one_ds))
                sys.exit(1)

        sets = [ds for ds in self.ordered if ds in dataset]  # enforce order

        self.stdout.write("Importing {}".format(", ".join(sets)))

        if options['validate']:
            validate_tables.check_table_targets()
            return

        for one_ds in sets:

            if options['run-import']:
                for job_class in self.imports[one_ds]:
                    batch.execute(job_class())

