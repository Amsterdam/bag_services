# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0009_redenafvoer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Eigendomsverhouding',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=4)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
