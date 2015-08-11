# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0042_lkisectie'),
    ]

    operations = [
        migrations.CreateModel(
            name='LkiKadastraalObject',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('kadastrale_gemeente_code', models.CharField(max_length=5)),
                ('sectie_code', models.CharField(max_length=2)),
                ('index_letter', models.CharField(max_length=1)),
                ('index_nummer', models.IntegerField()),
                ('oppervlakte', models.IntegerField()),
                ('ingang_cyclus', models.DateField()),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
