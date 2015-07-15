# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bron',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
