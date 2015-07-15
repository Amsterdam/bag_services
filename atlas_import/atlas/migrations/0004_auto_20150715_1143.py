# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0003_gemeente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gemeente',
            name='geldigheid_begin',
        ),
        migrations.RemoveField(
            model_name='gemeente',
            name='geldigheid_eind',
        ),
    ]
