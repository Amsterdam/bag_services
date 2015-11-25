# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0033_auto_20151125_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='buurt',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='buurt',
            name='buurtcombinatie',
            field=models.ForeignKey(to='bag.Buurtcombinatie', related_name='buurten', null=True),
        ),
        migrations.AddField(
            model_name='buurt',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='buurt',
            name='vollcode',
            field=models.CharField(max_length=4, default='XXX'),
            preserve_default=False,
        ),
    ]
