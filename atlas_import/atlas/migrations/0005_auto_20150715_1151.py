# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0004_auto_20150715_1143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gemeente',
            old_name='indicatie_vervallen',
            new_name='vervallen',
        ),
        migrations.RenameField(
            model_name='gemeente',
            old_name='indicatie_verzorgingsgebied',
            new_name='verzorgingsgebied',
        ),
        migrations.RemoveField(
            model_name='gemeente',
            name='gemeente_waarin_overgegaan',
        ),
        migrations.RemoveField(
            model_name='gemeente',
            name='mutatie_gebruiker',
        ),
    ]
