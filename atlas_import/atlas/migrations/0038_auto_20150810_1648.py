# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0037_auto_20150810_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lkigemeente',
            name='gemeentecode',
            field=models.BigIntegerField(),
        ),
    ]
