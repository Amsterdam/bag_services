# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0031_auto_20150805_1657'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beperking',
            old_name='beperkingcode',
            new_name='beperkingtype',
        ),
    ]
