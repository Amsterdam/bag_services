# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0057_auto_20150903_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verblijfsobject',
            name='nevenadressen',
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='ligplaats',
            field=models.ForeignKey(to='atlas.Ligplaats', null=True, related_name='adressen'),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='standplaats',
            field=models.ForeignKey(to='atlas.Standplaats', null=True, related_name='adressen'),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='verblijfsobject',
            field=models.ForeignKey(to='atlas.Verblijfsobject', null=True, related_name='adressen'),
        ),
        migrations.AlterField(
            model_name='ligplaats',
            name='hoofdadres',
            field=models.ForeignKey(to='atlas.Nummeraanduiding', null=True, related_name='+'),
        ),
        migrations.AlterField(
            model_name='standplaats',
            name='hoofdadres',
            field=models.ForeignKey(to='atlas.Nummeraanduiding', null=True, related_name='+'),
        ),
        migrations.AlterField(
            model_name='verblijfsobject',
            name='hoofdadres',
            field=models.ForeignKey(to='atlas.Nummeraanduiding', null=True, related_name='+'),
        ),
    ]
