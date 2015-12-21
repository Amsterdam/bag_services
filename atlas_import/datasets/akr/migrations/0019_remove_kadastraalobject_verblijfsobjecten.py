# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0018_auto_20151208_1603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kadastraalobject',
            name='verblijfsobjecten',
        ),
    ]
