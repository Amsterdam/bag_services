# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0029_auto_20160106_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastralegemeente',
            name='naam',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='zakelijkrecht',
            name='id',
            field=models.CharField(max_length=183, serialize=False, primary_key=True),
        ),
    ]
