# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0005_auto_20151214_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='overlijdensdatum',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
