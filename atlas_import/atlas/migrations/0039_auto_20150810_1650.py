# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0038_auto_20150810_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lkigemeente',
            name='gemeentecode',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='lkigemeente',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
