# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0026_auto_20151124_1158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ligplaats',
            name='landelijk_id',
            field=models.CharField(null=True, max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='standplaats',
            name='landelijk_id',
            field=models.CharField(null=True, max_length=16, unique=True),
        ),
    ]
