# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0054_auto_20150901_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verblijfsobjectpandrelatie',
            name='id',
            field=models.CharField(max_length=29, serialize=False, primary_key=True),
        ),
    ]
