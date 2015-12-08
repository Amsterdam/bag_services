# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0036_auto_20151207_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='openbareruimte',
            name='geometrie',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992, null=True),
        ),
    ]
