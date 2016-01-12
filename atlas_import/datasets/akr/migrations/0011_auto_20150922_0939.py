# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        # ('bag', '0003_auto_20150908_1255'),
        ('akr', '0010_auto_20150921_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastraalobject',
            name='verblijfsobjecten',
            field=models.ManyToManyField(to='bag.Verblijfsobject', through='akr.KadastraalObjectVerblijfsobject'),
        ),
        migrations.AlterField(
            model_name='kadastraalobjectverblijfsobject',
            name='kadastraal_object',
            field=models.ForeignKey(to='akr.KadastraalObject'),
        ),
        migrations.AlterField(
            model_name='kadastraalobjectverblijfsobject',
            name='verblijfsobject',
            field=models.ForeignKey(null=True, to='bag.Verblijfsobject'),
        ),
    ]
