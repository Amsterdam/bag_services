# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0009_auto_20150921_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kadastraalobjectverblijfsobject',
            name='vbo_id',
        ),
        migrations.AlterField(
            model_name='kadastraalobjectverblijfsobject',
            name='verblijfsobject',
            field=models.ForeignKey(to='bag.Verblijfsobject', related_name='kadastrale_objecten', null=True),
        ),
    ]
