# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0033_auto_20160321_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastraalobject',
            name='geom_point',
            field=django.contrib.gis.db.models.fields.PointField(srid=28992, null=True),
        ),
    ]
