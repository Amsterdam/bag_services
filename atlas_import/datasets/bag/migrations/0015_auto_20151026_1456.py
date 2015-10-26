# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0014_auto_20151026_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buurt',
            name='brondocument_naam',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
