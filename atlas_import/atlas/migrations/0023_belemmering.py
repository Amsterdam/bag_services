# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0022_auto_20150724_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='Belemmering',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=14, primary_key=True, serialize=False)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('inschrijfnummer', models.IntegerField()),
                ('beperkingcode', models.CharField(max_length=2)),
                ('datum_in_werking', models.DateTimeField(null=True)),
                ('datum_einde', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
