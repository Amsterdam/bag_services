# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0024_auto_20151221_1615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kadastraalobject',
            name='g_percelen',
        ),
    ]
