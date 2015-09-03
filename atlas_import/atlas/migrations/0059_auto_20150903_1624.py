# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0058_auto_20150903_1536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verblijfsobjectnevenadresrelatie',
            name='nummeraanduiding',
        ),
        migrations.RemoveField(
            model_name='verblijfsobjectnevenadresrelatie',
            name='verblijfsobject',
        ),
        migrations.RemoveField(
            model_name='ligplaats',
            name='hoofdadres',
        ),
        migrations.RemoveField(
            model_name='standplaats',
            name='hoofdadres',
        ),
        migrations.RemoveField(
            model_name='verblijfsobject',
            name='hoofdadres',
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='is_hoofdadres',
            field=models.NullBooleanField(default=None),
        ),
        migrations.DeleteModel(
            name='VerblijfsobjectNevenadresRelatie',
        ),
    ]
