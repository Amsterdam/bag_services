# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0009_auto_20151214_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kadastraalobject',
            name='gemeente',
        ),
    ]
