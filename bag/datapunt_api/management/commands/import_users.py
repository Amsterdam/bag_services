from django.core.management import BaseCommand

import logging

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv_file")

    def handle(self, *args, **options):
        log.error('DEPRICATED!! import_users..')
        pass
