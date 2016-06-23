import csv

import datetime
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.utils.timezone import UTC

from datasets.brk import models as brk_models


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("csv_file")

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        view_sensitive_details_permission_brk = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(brk_models.KadastraalSubject),
            codename='view_sensitive_details'
        )

        with open(csv_file) as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # skip header

            for row in reader:
                username = row[0].lower()
                password = row[1]
                email = row[2]
                joined = datetime.datetime.strptime(row[3], "%d-%m-%Y")
                joined = joined.replace(tzinfo=UTC())

                User.objects.filter(username=username).delete()
                user = User.objects.create_user(username=username, password=password, email=email)
                user.date_joined = joined
                user.user_permissions.add(view_sensitive_details_permission_brk)
                user.save()
