# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0011_auto_20151022_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='bouwblok',
            name='ingang_cyclus',
            field=models.DateField(null=True),
        ),
    ]
