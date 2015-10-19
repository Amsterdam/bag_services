# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0014_auto_20151008_1034'),
        ('wkpb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object_akr',
            field=models.ForeignKey(default=1, to='akr.KadastraalObject'),
            preserve_default=False,
        ),
    ]
