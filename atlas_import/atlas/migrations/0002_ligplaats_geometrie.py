# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ligplaats',
            name='geometrie',
            field=django.contrib.gis.db.models.fields.PolygonField(srid=28992, null=True),
        ),
    ]
