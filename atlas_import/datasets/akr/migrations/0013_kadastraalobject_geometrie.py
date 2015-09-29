# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0012_auto_20150922_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastraalobject',
            name='geometrie',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=28992),
        ),
    ]
