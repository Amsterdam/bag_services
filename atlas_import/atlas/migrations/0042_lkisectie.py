# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0041_auto_20150811_0929'),
    ]

    operations = [
        migrations.CreateModel(
            name='LkiSectie',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('kadastrale_gemeente_code', models.CharField(max_length=5)),
                ('code', models.CharField(max_length=2)),
                ('ingang_cyclus', models.DateField()),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
