# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0062_auto_20150908_1139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beperking',
            name='beperkingtype',
        ),
        migrations.RemoveField(
            model_name='beperkingkadastraalobject',
            name='beperking',
        ),
        migrations.RemoveField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object',
        ),
        migrations.RemoveField(
            model_name='wkpbbrondocument',
            name='bron',
        ),
        migrations.DeleteModel(
            name='Beperking',
        ),
        migrations.DeleteModel(
            name='Beperkingcode',
        ),
        migrations.DeleteModel(
            name='BeperkingKadastraalObject',
        ),
        migrations.DeleteModel(
            name='WkpbBroncode',
        ),
        migrations.DeleteModel(
            name='WkpbBrondocument',
        ),
    ]
