# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0006_auto_20150916_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='id',
            field=models.CharField(max_length=17, primary_key=True, serialize=False),
        ),
    ]
