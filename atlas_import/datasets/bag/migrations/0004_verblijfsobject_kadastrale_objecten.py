# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0011_auto_20150922_0939'),
        ('bag', '0003_auto_20150908_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='verblijfsobject',
            name='kadastrale_objecten',
            field=models.ManyToManyField(to='akr.KadastraalObject', through='akr.KadastraalObjectVerblijfsobject'),
        ),
    ]
