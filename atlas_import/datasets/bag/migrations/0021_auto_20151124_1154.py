# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0020_auto_20151124_1153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nummeraanduiding',
            old_name='code',
            new_name='landelijk_id',
        ),
    ]
