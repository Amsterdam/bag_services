# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0028_auto_20151124_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='verblijfsobject',
            name='verhuurbare_eenheden',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
