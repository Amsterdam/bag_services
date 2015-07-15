# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0002_auto_20150715_0919'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gemeente',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=4, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('gemeente_waarin_overgegaan', models.CharField(null=True, max_length=4)),
                ('indicatie_verzorgingsgebied', models.BooleanField(default=False)),
                ('mutatie_gebruiker', models.CharField(null=True, max_length=30)),
                ('indicatie_vervallen', models.BooleanField(default=False)),
                ('geldigheid_begin', models.DateField()),
                ('geldigheid_eind', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
