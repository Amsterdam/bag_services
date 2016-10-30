import csv
import datetime

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.utils.timezone import UTC

from datasets.brk import models as brk_models


class Command(BaseCommand):
    view_sensitive_details_permission_brk = Permission.objects.get(
        content_type=ContentType.objects.get_for_model(
            brk_models.KadastraalSubject),
        codename='view_sensitive_details'
    )

    def add_arguments(self, parser):
        parser.add_argument("csv_file")

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file) as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # skip header

            for row in reader:
                username = row[0].lower()
                joined = datetime.datetime.strptime(row[1], "%d-%m-%Y").replace(
                    tzinfo=UTC())
                self.create_user(username, joined)

    def create_user(self, username, joined):
        User.objects.filter(username=username).delete()
        user = User.objects.create_user(username=username)
        user.date_joined = joined
        user.user_permissions.add(self.view_sensitive_details_permission_brk)
        user.save()
