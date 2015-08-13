# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0044_auto_20150811_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='lkikadastraalobject',
            name='aanduiding',
            field=models.CharField(default='', max_length=17),
            preserve_default=False,
        ),
    ]
