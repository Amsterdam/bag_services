# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0039_auto_20151209_1602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verblijfsobject',
            options={'verbose_name': 'Verblijfsobject', 'verbose_name_plural': 'Verblijfsobjecten', 'ordering': ('_openbare_ruimte_naam', '_huisnummer', '_huisletter', '_huisnummer_toevoeging')},
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='_huisletter',
            field=models.CharField(max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='_huisnummer',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='_huisnummer_toevoeging',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='_openbare_ruimte_naam',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='hoofdadres',
            field=models.NullBooleanField(default=None),
        ),
    ]
