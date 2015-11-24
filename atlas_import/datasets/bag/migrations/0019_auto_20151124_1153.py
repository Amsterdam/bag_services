# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0018_auto_20151104_1203'),
    ]

    operations = [
        migrations.RenameField(
            model_name='woonplaats',
            old_name='code',
            new_name='landelijk_id',
        ),
    ]
