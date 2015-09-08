# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gemeente',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('gemeentecode', models.IntegerField()),
                ('gemeentenaam', models.CharField(max_length=9)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraalObject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('kadastrale_gemeente_code', models.CharField(max_length=5)),
                ('sectie_code', models.CharField(max_length=2)),
                ('perceelnummer', models.IntegerField()),
                ('indexletter', models.CharField(max_length=1)),
                ('indexnummer', models.IntegerField()),
                ('oppervlakte', models.IntegerField()),
                ('ingang_cyclus', models.DateField()),
                ('aanduiding', models.CharField(db_index=True, max_length=17)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraleGemeente',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('code', models.CharField(max_length=5)),
                ('ingang_cyclus', models.DateField()),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sectie',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('kadastrale_gemeente_code', models.CharField(max_length=5)),
                ('code', models.CharField(max_length=2)),
                ('ingang_cyclus', models.DateField()),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
