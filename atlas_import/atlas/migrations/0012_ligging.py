# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0011_financieringswijze'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ligging',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, max_length=4, serialize=False)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
