# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0024_auto_20150805_1044'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Belemmeringcode',
            new_name='Beperkingcode',
        ),
    ]
