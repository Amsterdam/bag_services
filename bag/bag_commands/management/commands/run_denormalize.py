"""
Database denormalize commands
"""

import sys

from django.core.management import BaseCommand
from django.db import connection

import datasets.bag.batch
import datasets.brk.batch
from datasets import validate_tables
from batch import batch


class Command(BaseCommand):
    """
    denormalize data
    """

    def handle(self, *args, **options):

        self.stdout.write("Denormalizing")
        batch.execute(datasets.bag.batch.DenormalizeBagJob())

        # analyze database after job
        with connection.cursor() as cur:
            self.stdout.write("Analyzing database...")
            cur.execute("VACUUM ANALYZE")
