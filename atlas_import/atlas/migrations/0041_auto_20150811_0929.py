# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0040_lkikadastralegemeente'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lkikadastralegemeente',
            old_name='datum_ingang',
            new_name='ingang_cyclus',
        ),
    ]
