# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0027_auto_20160105_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastralegemeente',
            name='naam',
            field=models.CharField(max_length=100, default='', serialize=False),
            preserve_default=False,
        ),
    ]
