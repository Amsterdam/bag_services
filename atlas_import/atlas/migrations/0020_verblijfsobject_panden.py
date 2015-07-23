# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0019_add_vbo_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='verblijfsobject',
            name='panden',
            field=models.ManyToManyField(to='atlas.Pand', related_name='verblijfsobjecten'),
        ),
    ]
