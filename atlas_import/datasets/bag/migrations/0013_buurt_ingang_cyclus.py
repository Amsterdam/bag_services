# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0012_bouwblok_ingang_cyclus'),
    ]

    operations = [
        migrations.AddField(
            model_name='buurt',
            name='ingang_cyclus',
            field=models.DateField(null=True),
        ),
    ]
