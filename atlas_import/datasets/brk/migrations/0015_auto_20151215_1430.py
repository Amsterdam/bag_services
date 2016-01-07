# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0014_auto_20151215_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='aanduiding',
            field=models.CharField(max_length=17),
        ),
    ]
