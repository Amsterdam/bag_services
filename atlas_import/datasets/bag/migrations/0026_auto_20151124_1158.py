# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0025_auto_20151124_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ligplaats',
            name='landelijk_id',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='landelijk_id',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='pand',
            name='landelijk_id',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='standplaats',
            name='landelijk_id',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='verblijfsobject',
            name='landelijk_id',
            field=models.CharField(max_length=16, unique=True),
        ),
    ]
