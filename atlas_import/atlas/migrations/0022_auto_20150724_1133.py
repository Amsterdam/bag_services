# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0021_add_sta_lig_view'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pand',
            name='hoogste_bouwlaag',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='pand',
            name='laagste_bouwlaag',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='verblijfsobject',
            name='bouwlaag_toegang',
            field=models.IntegerField(null=True),
        ),
    ]
