# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0011_auto_20150922_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='verblijfsobjecten',
            field=models.ManyToManyField(through='akr.KadastraalObjectVerblijfsobject', related_name='kadastrale_objecten', to='bag.Verblijfsobject'),
        ),
    ]
