# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0015_auto_20151013_1158'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kadastraalobject',
            options={'verbose_name': 'Kadastraal object', 'verbose_name_plural': 'Kadastrale objecten', 'ordering': ('objectindex_letter', 'objectindex_nummer', 'id')},
        ),
    ]
