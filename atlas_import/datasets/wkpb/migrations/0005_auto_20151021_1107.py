# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0015_auto_20151013_1158'),
        ('wkpb', '0004_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='beperking',
            name='kadastrale_objecten',
            field=models.ManyToManyField(to='akr.KadastraalObject', through='wkpb.BeperkingKadastraalObject', related_name='beperkingen'),
        ),
        migrations.AlterField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object_akr',
            field=models.ForeignKey(to='akr.KadastraalObject'),
        ),
    ]
