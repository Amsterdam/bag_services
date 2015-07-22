# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0015_toegang'),
    ]

    operations = [
        migrations.CreateModel(
            name='Verblijfsobject',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('gebruiksdoel_code', models.CharField(max_length=4, null=True)),
                ('gebruiksdoel_omschrijving', models.CharField(max_length=150, null=True)),
                ('oppervlakte', models.PositiveIntegerField(null=True)),
                ('bouwlaag_toegang', models.PositiveIntegerField(null=True)),
                ('status_coordinaat_code', models.CharField(max_length=3, null=True)),
                ('status_coordinaat_omschrijving', models.CharField(max_length=150, null=True)),
                ('bouwlagen', models.PositiveIntegerField(null=True)),
                ('type_woonobject_code', models.CharField(max_length=2, null=True)),
                ('type_woonobject_omschrijving', models.CharField(max_length=150, null=True)),
                ('woningvoorraad', models.BooleanField(default=False)),
                ('aantal_kamers', models.PositiveIntegerField(null=True)),
                ('vervallen', models.PositiveIntegerField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PointField(null=True, srid=28992)),
                ('bron', models.ForeignKey(null=True, to='atlas.Bron')),
                ('buurt', models.ForeignKey(null=True, to='atlas.Buurt')),
                ('eigendomsverhouding', models.ForeignKey(null=True, to='atlas.Eigendomsverhouding')),
                ('financieringswijze', models.ForeignKey(null=True, to='atlas.Financieringswijze')),
                ('gebruik', models.ForeignKey(null=True, to='atlas.Gebruik')),
                ('ligging', models.ForeignKey(null=True, to='atlas.Ligging')),
                ('locatie_ingang', models.ForeignKey(null=True, to='atlas.LocatieIngang')),
                ('reden_afvoer', models.ForeignKey(null=True, to='atlas.RedenAfvoer')),
                ('status', models.ForeignKey(null=True, to='atlas.Status')),
                ('toegang', models.ForeignKey(null=True, to='atlas.Toegang')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
