# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0001_squashed_0042_auto_20151210_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gebiedsgerichtwerken',
            name='id',
            field=models.CharField(primary_key=True, serialize=False, max_length=4),
        ),
        migrations.AlterField(
            model_name='grootstedelijkgebied',
            name='id',
            field=models.SlugField(primary_key=True, serialize=False, max_length=100),
        ),
        migrations.AlterField(
            model_name='unesco',
            name='id',
            field=models.SlugField(primary_key=True, serialize=False, max_length=100),
        ),
    ]
