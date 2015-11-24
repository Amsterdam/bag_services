# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0019_auto_20151124_1153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ligplaats',
            old_name='identificatie',
            new_name='landelijk_id',
        ),
    ]
