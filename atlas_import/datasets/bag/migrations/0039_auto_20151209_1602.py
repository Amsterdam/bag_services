# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0038_auto_20151208_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='hoofdadres',
            field=models.NullBooleanField(default=None, db_index=True),
        ),
    ]
