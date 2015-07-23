# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0016_verblijfsobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='verblijfsobject',
            name='hoofdadres',
            field=models.ForeignKey(null=True, to='atlas.Nummeraanduiding', related_name='verblijfsobjecten'),
        ),
    ]
