# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wkpb', '0002_beperkingkadastraalobject_kadastraal_object_akr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object_akr',
            field=models.ForeignKey(to='akr.KadastraalObject', related_name='beperkingen'),
        ),
    ]
