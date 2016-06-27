# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0002_auto_20160119_1248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nummeraanduiding',
            options={'verbose_name_plural': 'Nummeraanduidingen', 'ordering': ('_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging'), 'verbose_name': 'Nummeraanduiding'},
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='_openbare_ruimte_naam',
            field=models.CharField(null=True, max_length=150),
        ),
        migrations.AlterIndexTogether(
            name='nummeraanduiding',
            index_together=set([('_openbare_ruimte_naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging')]),
        ),
    ]
