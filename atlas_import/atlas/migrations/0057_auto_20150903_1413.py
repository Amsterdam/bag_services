# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0056_auto_20150903_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verblijfsobjectnevenadresrelatie',
            name='id',
            field=models.CharField(serialize=False, primary_key=True, max_length=29),
        ),
    ]
