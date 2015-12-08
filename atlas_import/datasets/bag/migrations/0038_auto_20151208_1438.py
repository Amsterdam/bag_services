# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0037_openbareruimte_geometrie'),
    ]

    operations = [
        migrations.AddField(
            model_name='gemeente',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='gemeente',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
    ]
