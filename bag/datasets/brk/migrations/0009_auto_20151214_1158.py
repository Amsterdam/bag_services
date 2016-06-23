# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0008_auto_20151214_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='voornaamste_gerechtigde',
            field=models.ForeignKey(null=True, to='brk.KadastraalSubject'),
        ),
    ]
