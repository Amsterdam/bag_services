import time

from django.conf import settings
from django.core.management import BaseCommand

import datasets.bag.batch
import datasets.brk.batch
import datasets.wkpb.batch
from batch import batch


class Command(BaseCommand):
    ordered = ['bag', 'brk', 'wkpb', 'gebieden']

    indexes = {
        'bag': [datasets.bag.batch.BuildIndexBagJob],
        'brk': [datasets.brk.batch.BuildIndexKadasterJob],
        'wkpb': [],
        'gebieden': [datasets.bag.batch.IndexGebiedenJob],
    }

    delete_indexes = {
        'bag': [datasets.bag.batch.DeleteIndexBagJob],
        'brk': [datasets.brk.batch.DeleteIndexKadasterJob],
        # 'brk': [],
        'wkpb': [],  # has no elastic index
        'gebieden': [datasets.bag.batch.DeleteIndexGebiedJob],
    }

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to use, choose from {}".format(
                ', '.join(self.indexes.keys())))

        parser.add_argument(
            '--build',
            action='store_true',
            dest='build_index',
            default=False,
            help='Build elastic index from postgres')

        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete_indexes',
            default=False,
            help='Delete elastic indexes from elastic')

        parser.add_argument(
            '--partial',
            action='store',
            dest='partial_index',
            default=0,
            help='Build X/Y parts 1/3, 2/3, 3/3')

    def set_partial_config(self, options):
        """
        Do partial configuration
        """
        if options['partial_index']:
            numerator, denominator = options['partial_index'].split('/')

            numerator = int(numerator) - 1
            denominator = int(denominator)

            assert (numerator < denominator)

            settings.PARTIAL_IMPORT['numerator'] = numerator
            settings.PARTIAL_IMPORT['denominator'] = denominator

    def handle(self, *args, **options):

        dataset = options['dataset']

        start = time.time()

        for ds in dataset:
            if ds not in self.indexes.keys():
                self.stderr.write("Unkown dataset: {}".format(ds))
                return

        sets = [ds for ds in self.ordered if ds in dataset]  # enforce order

        self.stdout.write("Working on {}".format(", ".join(sets)))

        self.set_partial_config(options)

        for ds in sets:

            if options['delete_indexes']:
                for job_class in self.delete_indexes[ds]:
                    batch.execute(job_class())
                # we do not run the other tasks
                continue  # to next dataset please..

            if options['build_index']:
                for job_class in self.indexes[ds]:
                    batch.execute(job_class(), )

        self.stdout.write(
            "Total Duration: %.2f seconds" % (time.time() - start))
