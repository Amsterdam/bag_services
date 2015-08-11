# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0043_lkikadastraalobject'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lkikadastraalobject',
            old_name='index_letter',
            new_name='indexletter',
        ),
        migrations.RenameField(
            model_name='lkikadastraalobject',
            old_name='index_nummer',
            new_name='indexnummer',
        ),
        migrations.AddField(
            model_name='lkikadastraalobject',
            name='perceelnummer',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
