# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0041_auto_20151209_1702'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ligplaats',
            options={'verbose_name_plural': 'Ligplaatsen', 'verbose_name': 'Ligplaats', 'ordering': ('_openbare_ruimte_naam', '_huisnummer', '_huisletter', '_huisnummer_toevoeging')},
        ),
        migrations.AlterModelOptions(
            name='standplaats',
            options={'verbose_name_plural': 'Standplaatsen', 'verbose_name': 'Standplaats', 'ordering': ('_openbare_ruimte_naam', '_huisnummer', '_huisletter', '_huisnummer_toevoeging')},
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='_huisletter',
            field=models.CharField(null=True, max_length=1),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='_huisnummer',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='_huisnummer_toevoeging',
            field=models.CharField(null=True, max_length=4),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='_openbare_ruimte_naam',
            field=models.CharField(null=True, max_length=150),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='_huisletter',
            field=models.CharField(null=True, max_length=1),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='_huisnummer',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='_huisnummer_toevoeging',
            field=models.CharField(null=True, max_length=4),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='_openbare_ruimte_naam',
            field=models.CharField(null=True, max_length=150),
        ),
        migrations.AlterIndexTogether(
            name='ligplaats',
            index_together=set([('_openbare_ruimte_naam', '_huisnummer', '_huisletter', '_huisnummer_toevoeging')]),
        ),
        migrations.AlterIndexTogether(
            name='standplaats',
            index_together=set([('_openbare_ruimte_naam', '_huisnummer', '_huisletter', '_huisnummer_toevoeging')]),
        ),
    ]
