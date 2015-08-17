# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0046_add_beperking_lkikadastraalobject_view'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lkikadastraalobject',
            name='aanduiding',
            field=models.CharField(max_length=17, db_index=True),
        ),
    ]
