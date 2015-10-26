# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0015_auto_20151026_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='buurtcombinatie',
            name='brondocument_datum',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='buurtcombinatie',
            name='brondocument_naam',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='buurtcombinatie',
            name='ingang_cyclus',
            field=models.DateField(null=True),
        ),
    ]
