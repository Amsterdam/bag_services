# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0013_kadastraalobject_geometrie'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kadastraalobject',
            options={'verbose_name': 'Kadastraal object', 'ordering': ('id',), 'verbose_name_plural': 'Kadastrale objecten'},
        ),
    ]
