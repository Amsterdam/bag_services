# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0006_auto_20150722_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='ligplaats',
            name='hoofdadres',
            field=models.ForeignKey(null=True, to='atlas.Nummeraanduiding', related_name='ligplaatsen'),
        ),
    ]
