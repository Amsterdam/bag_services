# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0023_auto_20151124_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='openbareruimte',
            name='landelijk_id',
            field=models.CharField(max_length=16, unique=True, null=True),
        ),
    ]
