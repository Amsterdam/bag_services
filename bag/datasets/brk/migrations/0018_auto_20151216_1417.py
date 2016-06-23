# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0017_auto_20151216_1315'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kadastraalsubject',
            options={'verbose_name': 'Kadastraal subject', 'verbose_name_plural': 'Kadastrale subjecten', 'permissions': (('brk.view_sensitive_details', 'Kan privacy-gevoelige data inzien'),)},
        ),
    ]
