# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0008_auto_20151008_1034'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bouwblok',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('code', models.CharField(max_length=4, unique=True)),
            ],
            options={
                'verbose_name': 'Bouwblok',
                'verbose_name_plural': 'Bouwblokken',
            },
        ),
        migrations.AddField(
            model_name='buurt',
            name='geometrie',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992),
        ),
        migrations.AddField(
            model_name='stadsdeel',
            name='geometrie',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992),
        ),
        migrations.AddField(
            model_name='bouwblok',
            name='buurt',
            field=models.ForeignKey(to='bag.Buurt'),
        ),
    ]
