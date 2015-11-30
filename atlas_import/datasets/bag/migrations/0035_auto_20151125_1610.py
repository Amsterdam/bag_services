# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0034_auto_20151125_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='bouwblok',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='bouwblok',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
    ]
