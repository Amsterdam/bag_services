# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0002_kadastralesectie_sectie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='geboortedatum',
            field=models.CharField(max_length=50, default=''),
            preserve_default=False,
        ),
    ]
