# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0022_auto_20151221_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='verblijfsobjecten',
            field=models.ManyToManyField(to='bag.Verblijfsobject',
                                         related_name='kadastrale_objecten',
                                         through='brk.KadastraalObjectVerblijfsobjectRelatie'),
        ),
    ]
