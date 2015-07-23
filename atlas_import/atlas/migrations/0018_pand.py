# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0017_verblijfsobject_hoofdadres'),
    ]

    operations = [
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
                ('laagste_bouwlaag', models.PositiveIntegerField(null=True)),
                ('hoogste_bouwlaag', models.PositiveIntegerField(null=True)),
                ('pandnummer', models.CharField(max_length=10, null=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(srid=28992, null=True)),
                ('status', models.ForeignKey(to='atlas.Status', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
