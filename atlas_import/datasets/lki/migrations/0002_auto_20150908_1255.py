# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lki', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gemeente',
            options={'verbose_name_plural': 'Gemeentes', 'verbose_name': 'Gemeente'},
        ),
        migrations.AlterModelOptions(
            name='kadastraalobject',
            options={'verbose_name_plural': 'Kadastrale Objecten', 'verbose_name': 'Kadastraal Object'},
        ),
        migrations.AlterModelOptions(
            name='kadastralegemeente',
            options={'verbose_name_plural': 'Kadastrale Gemeentes', 'verbose_name': 'Kadastrale Gemeente'},
        ),
        migrations.AlterModelOptions(
            name='sectie',
            options={'verbose_name_plural': 'Secties', 'verbose_name': 'Sectie'},
        ),
    ]
