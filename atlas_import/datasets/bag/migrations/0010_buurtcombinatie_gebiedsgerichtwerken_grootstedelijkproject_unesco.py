# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0009_auto_20151020_1804'),
    ]

    operations = [
        migrations.CreateModel(
            name='Buurtcombinatie',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('naam', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=2)),
                ('vollcode', models.CharField(max_length=3)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
            ],
            options={
                'verbose_name': 'Buurtcombinatie',
                'verbose_name_plural': 'Buurtcombinaties',
            },
        ),
        migrations.CreateModel(
            name='Gebiedsgerichtwerken',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('naam', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=4)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
                ('stadsdeel', models.ForeignKey(to='bag.Stadsdeel')),
            ],
            options={
                'verbose_name': 'Gebiedsgerichtwerken',
                'verbose_name_plural': 'Gebiedsgerichtwerken',
            },
        ),
        migrations.CreateModel(
            name='GrootstedelijkProject',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('naam', models.CharField(max_length=100)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
            ],
            options={
                'verbose_name': 'Grootstedelijk project',
                'verbose_name_plural': 'Grootstedelijk projecten',
            },
        ),
        migrations.CreateModel(
            name='Unesco',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('naam', models.CharField(max_length=100)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
            ],
            options={
                'verbose_name': 'Unesco',
                'verbose_name_plural': 'Unesco',
            },
        ),
    ]
