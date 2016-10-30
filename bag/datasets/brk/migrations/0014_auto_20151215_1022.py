# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0013_auto_20151214_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='grootte',
            field=models.IntegerField(null=True),
        ),
    ]
