# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0023_belemmering'),
    ]

    operations = [
        migrations.CreateModel(
            name='Belemmeringcode',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=4, serialize=False, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Belemmering',
        ),
    ]
