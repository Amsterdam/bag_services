# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0013_buurt_ingang_cyclus'),
    ]

    operations = [
        migrations.AddField(
            model_name='buurt',
            name='brondocument_datum',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='buurt',
            name='brondocument_naam',
            field=models.CharField(null=True, max_length=20),
        ),
    ]
