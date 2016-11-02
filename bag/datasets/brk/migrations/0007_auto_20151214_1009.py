# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0006_auto_20151214_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='geboortedatum',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='geboorteplaats',
            field=models.CharField(max_length=80, null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='overlijdensdatum',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='partner_naam',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='partner_voornamen',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='partner_voorvoegsels',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
