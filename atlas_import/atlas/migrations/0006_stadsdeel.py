# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0005_auto_20150715_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stadsdeel',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=14, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('vervallen', models.BooleanField(default=False)),
                ('gemeente', models.ForeignKey(to='atlas.Gemeente')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
