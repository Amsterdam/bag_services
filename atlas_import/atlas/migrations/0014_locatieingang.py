# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0013_gebruik'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocatieIngang',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
