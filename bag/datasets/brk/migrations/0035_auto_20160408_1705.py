# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0034_kadastraalobject_geom_point'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kadastraalobject',
            old_name='geom_point',
            new_name='point_geom',
        ),
        migrations.RenameField(
            model_name='kadastraalobject',
            old_name='geometrie',
            new_name='poly_geom',
        ),
    ]
