"""
Database import commands
"""

import sys

from django.core.management import BaseCommand

import datasets.bag.batch
import datasets.brk.batch
import datasets.brk.batch_gob
import datasets.wkpb.batch
import datasets.wkpb.batch_gob
from datasets import validate_tables
from batch import batch


class Command(BaseCommand):
    """
    Import datainto database. with options to select dataset
    """
    ordered = [
        'bag',
        'gebieden',
        'brk',
        'wkpb',
    ]

    imports = dict(
        bag=[datasets.bag.batch.ImportBagJob],
        brk=[datasets.brk.batch.ImportKadasterJob],
        wkpb=[datasets.wkpb.batch.ImportWkpbJob],
        gebieden=[],
    )

    imports_gob = dict(
        bag=[datasets.bag.batch.ImportBagJob],
        brk=[datasets.brk.batch_gob.ImportKadasterJob],
        wkpb=[datasets.wkpb.batch_gob.ImportWkpbJob],
        gebieden=[],
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

        parser.add_argument(
            '--gob',
            '-g',
            action='store_true',
            dest='gob',
            default=False,
            help='Use GOB for import'
        )

    def handle(self, *args, **options):
        dataset = options['dataset']

        if options['gob']:
            self.imports = self.imports_gob

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
            for job_class in self.imports[one_ds]:
                batch.execute(job_class())

