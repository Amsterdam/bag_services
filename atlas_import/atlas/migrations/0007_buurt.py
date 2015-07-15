# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0006_stadsdeel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Buurt',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=14, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('vervallen', models.BooleanField(default=False)),
                ('stadsdeel', models.ForeignKey(to='atlas.Stadsdeel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
