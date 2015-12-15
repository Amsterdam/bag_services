# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0011_auto_20151214_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='beperkt_tot_tng',
        ),
    ]
