# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0003_auto_20150722_0826'),
    ]

    operations = [
        migrations.CreateModel(
            name='Woonplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(null=True, max_length=20)),
                ('id', models.CharField(primary_key=True, max_length=14, serialize=False)),
                ('code', models.CharField(max_length=4, unique=True)),
                ('naam', models.CharField(max_length=80)),
                ('naam_ptt', models.CharField(null=True, max_length=18)),
                ('vervallen', models.BooleanField(default=False)),
                ('gemeente', models.ForeignKey(to='atlas.Gemeente')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
