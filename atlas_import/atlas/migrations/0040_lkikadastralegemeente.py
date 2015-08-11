# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0039_auto_20150810_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='LkiKadastraleGemeente',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=5)),
                ('datum_ingang', models.DateField()),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
