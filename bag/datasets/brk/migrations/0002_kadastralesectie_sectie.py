# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastralesectie',
            name='sectie',
            field=models.CharField(max_length=2, default='A'),
            preserve_default=False,
        ),
    ]
