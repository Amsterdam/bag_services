# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0017_auto_20151208_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastraalobject',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
    ]
