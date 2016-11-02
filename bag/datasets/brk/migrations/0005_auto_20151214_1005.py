# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0004_auto_20151214_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='postadres',
            field=models.ForeignKey(null=True, related_name='+', to='brk.Adres'),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='woonadres',
            field=models.ForeignKey(null=True, related_name='+', to='brk.Adres'),
        ),
    ]
