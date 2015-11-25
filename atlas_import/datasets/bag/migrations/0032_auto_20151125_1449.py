# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0031_auto_20151125_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='buurtcombinatie',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='buurtcombinatie',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='buurtcombinatie',
            name='stadsdeel',
            field=models.ForeignKey(to='bag.Stadsdeel', null=True, related_name='buurtcombinaties'),
        ),
    ]
