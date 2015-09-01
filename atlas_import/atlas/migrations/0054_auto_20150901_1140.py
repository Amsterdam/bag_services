# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0053_auto_20150901_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='verblijfsobject',
            old_name='panden_tmp',
            new_name='panden',
        ),
    ]
