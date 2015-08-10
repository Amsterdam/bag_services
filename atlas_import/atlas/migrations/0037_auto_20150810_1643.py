# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0036_lkigemeente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lkigemeente',
            name='geometrie',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992, null=True),
        ),
    ]
