# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0016_auto_20151207_1533'),
    ]

    operations = [
        migrations.AddField(
            model_name='zakelijkrecht',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
    ]
