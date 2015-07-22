# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0007_ligplaats_hoofdadres'),
    ]

    operations = [
        migrations.CreateModel(
            name='Standplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(max_length=14, primary_key=True, serialize=False)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(null=True, srid=28992)),
                ('bron', models.ForeignKey(null=True, to='atlas.Bron')),
                ('buurt', models.ForeignKey(null=True, to='atlas.Buurt')),
                ('hoofdadres', models.ForeignKey(to='atlas.Nummeraanduiding', related_name='standplaatsen', null=True)),
                ('status', models.ForeignKey(null=True, to='atlas.Status')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
