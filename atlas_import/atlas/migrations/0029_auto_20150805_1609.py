# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0028_auto_20150805_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wkpbbrondocument',
            name='documentnaam',
            field=models.CharField(max_length=21),
        ),
    ]
