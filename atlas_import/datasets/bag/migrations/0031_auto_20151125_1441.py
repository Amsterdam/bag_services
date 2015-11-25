# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0030_pand_bouwblok'),
    ]

    operations = [
        migrations.AddField(
            model_name='stadsdeel',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='stadsdeel',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='pand',
            name='bouwblok',
            field=models.ForeignKey(to='bag.Bouwblok', related_name='panden', null=True),
        ),
    ]
