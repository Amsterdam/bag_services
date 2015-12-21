# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wkpb', '0009_auto_20151209_1340'),
        ('geo_views', '0009_bag_opr_view'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP VIEW IF EXISTS geo_wkpb",
        ),
        migrations.RunSQL(
            sql="DELETE FROM wkpb_beperkingkadastraalobject",
        ),
        migrations.RemoveField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object_akr',
        ),
        migrations.AlterField(
            model_name='beperking',
            name='kadastrale_objecten',
            field=models.ManyToManyField(related_name='beperkingen', to='brk.KadastraalObject', through='wkpb.BeperkingKadastraalObject'),
        ),
        migrations.AlterField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object',
            field=models.ForeignKey(to='brk.KadastraalObject'),
        ),
    ]
