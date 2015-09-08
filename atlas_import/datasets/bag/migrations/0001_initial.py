# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datasets.bag.models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bron',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Buurt',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('vervallen', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Eigendomsverhouding',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Financieringswijze',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gebruik',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gemeente',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(max_length=4, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('verzorgingsgebied', models.BooleanField(default=False)),
                ('vervallen', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ligging',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ligplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(null=True, srid=28992)),
                ('bron', models.ForeignKey(null=True, to='bag.Bron')),
                ('buurt', models.ForeignKey(null=True, to='bag.Buurt')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, datasets.bag.models.AdresseerbaarObjectMixin),
        ),
        migrations.CreateModel(
            name='LocatieIngang',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Nummeraanduiding',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(max_length=14, unique=True)),
                ('huisnummer', models.CharField(max_length=5)),
                ('huisletter', models.CharField(max_length=1, null=True)),
                ('huisnummer_toevoeging', models.CharField(max_length=4, null=True)),
                ('postcode', models.CharField(max_length=6, null=True)),
                ('type', models.CharField(max_length=2, choices=[('01', 'Verblijfsobject'), ('02', 'Standplaats'), ('03', 'Ligplaats'), ('04', 'Overig gebouwd object'), ('05', 'Overig terrein')], null=True)),
                ('adres_nummer', models.CharField(max_length=10, null=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('hoofdadres', models.NullBooleanField(default=None)),
                ('bron', models.ForeignKey(null=True, to='bag.Bron')),
                ('ligplaats', models.ForeignKey(to='bag.Ligplaats', related_name='adressen', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OpenbareRuimte',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('type', models.CharField(max_length=2, choices=[('01', 'Weg'), ('02', 'Water'), ('03', 'Spoorbaan'), ('04', 'Terrein'), ('05', 'Kunstwerk'), ('06', 'Landschappelijk gebied'), ('07', 'Administratief gebied')], null=True)),
                ('naam', models.CharField(max_length=150)),
                ('code', models.CharField(max_length=5, unique=True)),
                ('straat_nummer', models.CharField(max_length=10, null=True)),
                ('naam_nen', models.CharField(max_length=24)),
                ('naam_ptt', models.CharField(max_length=17)),
                ('vervallen', models.BooleanField(default=False)),
                ('bron', models.ForeignKey(null=True, to='bag.Bron')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pand',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('bouwjaar', models.PositiveIntegerField(null=True)),
                ('laagste_bouwlaag', models.IntegerField(null=True)),
                ('hoogste_bouwlaag', models.IntegerField(null=True)),
                ('pandnummer', models.CharField(max_length=10, null=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(null=True, srid=28992)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RedenAfvoer',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stadsdeel',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('vervallen', models.BooleanField(default=False)),
                ('gemeente', models.ForeignKey(to='bag.Gemeente')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Standplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(null=True, srid=28992)),
                ('bron', models.ForeignKey(null=True, to='bag.Bron')),
                ('buurt', models.ForeignKey(null=True, to='bag.Buurt')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, datasets.bag.models.AdresseerbaarObjectMixin),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Toegang',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, primary_key=True, max_length=4)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Verblijfsobject',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('gebruiksdoel_code', models.CharField(max_length=4, null=True)),
                ('gebruiksdoel_omschrijving', models.CharField(max_length=150, null=True)),
                ('oppervlakte', models.PositiveIntegerField(null=True)),
                ('bouwlaag_toegang', models.IntegerField(null=True)),
                ('status_coordinaat_code', models.CharField(max_length=3, null=True)),
                ('status_coordinaat_omschrijving', models.CharField(max_length=150, null=True)),
                ('bouwlagen', models.PositiveIntegerField(null=True)),
                ('type_woonobject_code', models.CharField(max_length=2, null=True)),
                ('type_woonobject_omschrijving', models.CharField(max_length=150, null=True)),
                ('woningvoorraad', models.BooleanField(default=False)),
                ('aantal_kamers', models.PositiveIntegerField(null=True)),
                ('vervallen', models.PositiveIntegerField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PointField(null=True, srid=28992)),
                ('bron', models.ForeignKey(null=True, to='bag.Bron')),
                ('buurt', models.ForeignKey(null=True, to='bag.Buurt')),
                ('eigendomsverhouding', models.ForeignKey(null=True, to='bag.Eigendomsverhouding')),
                ('financieringswijze', models.ForeignKey(null=True, to='bag.Financieringswijze')),
                ('gebruik', models.ForeignKey(null=True, to='bag.Gebruik')),
                ('ligging', models.ForeignKey(null=True, to='bag.Ligging')),
                ('locatie_ingang', models.ForeignKey(null=True, to='bag.LocatieIngang')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, datasets.bag.models.AdresseerbaarObjectMixin),
        ),
        migrations.CreateModel(
            name='VerblijfsobjectPandRelatie',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=29)),
                ('pand', models.ForeignKey(to='bag.Pand')),
                ('verblijfsobject', models.ForeignKey(to='bag.Verblijfsobject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Woonplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(max_length=4, unique=True)),
                ('naam', models.CharField(max_length=80)),
                ('naam_ptt', models.CharField(max_length=18, null=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('gemeente', models.ForeignKey(to='bag.Gemeente')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='panden',
            field=models.ManyToManyField(related_name='verblijfsobjecten', through='bag.VerblijfsobjectPandRelatie', to='bag.Pand'),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='reden_afvoer',
            field=models.ForeignKey(null=True, to='bag.RedenAfvoer'),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='status',
            field=models.ForeignKey(null=True, to='bag.Status'),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='toegang',
            field=models.ForeignKey(null=True, to='bag.Toegang'),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='status',
            field=models.ForeignKey(null=True, to='bag.Status'),
        ),
        migrations.AddField(
            model_name='pand',
            name='status',
            field=models.ForeignKey(null=True, to='bag.Status'),
        ),
        migrations.AddField(
            model_name='openbareruimte',
            name='status',
            field=models.ForeignKey(null=True, to='bag.Status'),
        ),
        migrations.AddField(
            model_name='openbareruimte',
            name='woonplaats',
            field=models.ForeignKey(to='bag.Woonplaats'),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='openbare_ruimte',
            field=models.ForeignKey(to='bag.OpenbareRuimte'),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='standplaats',
            field=models.ForeignKey(to='bag.Standplaats', related_name='adressen', null=True),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='status',
            field=models.ForeignKey(null=True, to='bag.Status'),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='verblijfsobject',
            field=models.ForeignKey(to='bag.Verblijfsobject', related_name='adressen', null=True),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='status',
            field=models.ForeignKey(null=True, to='bag.Status'),
        ),
        migrations.AddField(
            model_name='buurt',
            name='stadsdeel',
            field=models.ForeignKey(to='bag.Stadsdeel'),
        ),
    ]
