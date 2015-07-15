# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0007_buurt'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ligplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('identificatie', models.DecimalField(max_digits=14, unique=True, decimal_places=0)),
                ('ligplaats_nummer', models.DecimalField(max_digits=10, unique=True, decimal_places=0)),
                ('vervallen', models.BooleanField(default=False)),
                ('bron', models.ForeignKey(null=True, to='atlas.Bron')),
                ('buurt', models.ForeignKey(null=True, to='atlas.Buurt')),
                ('status', models.ForeignKey(null=True, to='atlas.Status')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
