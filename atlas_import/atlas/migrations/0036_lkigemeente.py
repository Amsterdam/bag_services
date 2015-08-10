# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0035_beperking_kadastrale_aanduidingen'),
    ]

    operations = [
        migrations.CreateModel(
            name='LkiGemeente',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('gemeentecode', models.IntegerField()),
                ('gemeentenaam', models.CharField(max_length=9)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(srid=28992, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
