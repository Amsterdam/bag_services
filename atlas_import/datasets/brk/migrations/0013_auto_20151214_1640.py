# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0012_remove_zakelijkrecht_beperkt_tot_tng'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='belast_azt',
        ),
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='belast_met_azt',
        ),
    ]
