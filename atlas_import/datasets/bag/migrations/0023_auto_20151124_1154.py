# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0022_auto_20151124_1154'),
    ]

    operations = [
        migrations.RenameField(
            model_name='verblijfsobject',
            old_name='identificatie',
            new_name='landelijk_id',
        ),
    ]
