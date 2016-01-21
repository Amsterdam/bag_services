import sys
from django.core.management import BaseCommand

import datasets.bag.batch
import datasets.brk.batch
import datasets.wkpb.batch

from batch import batch
from batch.models import JobExecution


class Command(BaseCommand):

    ordered = ['bag', 'brk', 'wkpb']

    imports = dict(
        bag=[datasets.bag.batch.ImportBagJob],
        brk=[datasets.brk.batch.ImportKadasterJob],
        wkpb=[datasets.wkpb.batch.ImportWkpbJob],
    )

    indexes = dict(
        bag=[datasets.bag.batch.IndexJob],
        brk=[datasets.brk.batch.IndexKadasterJob],
        wkpb=[],
    )

    backup_indexes = dict(
        bag=[datasets.bag.batch.BackupBagJob],
        brk=[datasets.brk.batch.BackupKadasterJob],
        wkpb=[],
    )

    restore_indexes = dict(
        bag=[datasets.bag.batch.RestoreBagJob],
        brk=[datasets.brk.batch.RestoreKadasterJob],
        wkpb=[],
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'dataset',
            nargs='*',
            default=self.ordered,
            help="Dataset to import, choose from {}".format(
                ', '.join(self.imports.keys())))

        parser.add_argument('--backup-indexes-es',
                            action='store_true',
                            dest='backup_indexes_es',
                            default=False,
                            help='Backup elsatic search')

        parser.add_argument('--restore-indexes-es',
                            action='store_true',
                            dest='restore_indexes_es',
                            default=False,
                            help='Restore elsatic search index')

        parser.add_argument('--no-import',
                            action='store_false',
                            dest='run-import',
                            default=True,
                            help='Skip database importing')

        parser.add_argument('--no-index',
                            action='store_false',
                            dest='run-index',
                            default=True,
                            help='Skip elastic search indexing')

        parser.add_argument('--noinput', '--no-input',
                            action='store_false', dest='interactive', default=True,
                            help='Tells Django to NOT prompt the user for input of any kind.')

    def act_on_result(self, job_execution):
        if job_execution.status == JobExecution.STATUS_FAILED:
            self.stderr.write("Job {} failed, exiting".format(job_execution.name))
            sys.exit(1)

    def handle(self, *args, **options):
        dataset = options['dataset']

        for ds in dataset:
            if ds not in self.imports.keys():
                self.stderr.write("Unkown dataset: {}".format(ds))
                sys.exit(1)

        sets = [ds for ds in self.ordered if ds in dataset]     # enforce order

        self.stdout.write("Importing {}".format(", ".join(sets)))

        for ds in sets:

            if options['run-import']:
                for job_class in self.imports[ds]:
                    result = batch.execute(job_class())
                    self.act_on_result(result)

            if options['run-index']:
                for job_class in self.indexes[ds]:
                    result = batch.execute(job_class())
                    self.act_on_result(result)
