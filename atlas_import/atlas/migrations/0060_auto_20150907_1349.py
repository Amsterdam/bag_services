# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0059_auto_20150903_1624'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nummeraanduiding',
            old_name='is_hoofdadres',
            new_name='hoofdadres',
        ),
    ]
