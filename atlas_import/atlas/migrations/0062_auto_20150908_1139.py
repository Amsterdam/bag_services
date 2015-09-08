# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0061_auto_20150907_1623'),
        ('lki', '0001_initial')
    ]

    operations = [
        migrations.DeleteModel(
            name='LkiGemeente',
        ),
        migrations.DeleteModel(
            name='LkiKadastraleGemeente',
        ),
        migrations.DeleteModel(
            name='LkiSectie',
        ),
        migrations.AlterField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object',
            field=models.ForeignKey(to='lki.KadastraalObject'),
        ),
        migrations.DeleteModel(
            name='LkiKadastraalObject',
        ),
    ]
