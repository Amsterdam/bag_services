# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0025_auto_20150805_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='WkpbBroncode',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=4, primary_key=True, serialize=False)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
