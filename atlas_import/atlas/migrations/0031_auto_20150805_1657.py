# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0030_beperking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beperking',
            name='datum_einde',
        ),
        migrations.RemoveField(
            model_name='beperking',
            name='datum_in_werking',
        ),
    ]
