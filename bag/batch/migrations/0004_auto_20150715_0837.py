# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0003_auto_20150715_0757'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskexecution',
            options={'ordering': ('date_started',)},
        ),
    ]
