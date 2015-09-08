# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bron',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='buurt',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='eigendomsverhouding',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='financieringswijze',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='gebruik',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='gemeente',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='ligging',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='ligplaats',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='locatieingang',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='nummeraanduiding',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='openbareruimte',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='pand',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='redenafvoer',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='stadsdeel',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='standplaats',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='status',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='toegang',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='verblijfsobject',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='verblijfsobjectpandrelatie',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='woonplaats',
            name='date_created',
        ),
    ]
