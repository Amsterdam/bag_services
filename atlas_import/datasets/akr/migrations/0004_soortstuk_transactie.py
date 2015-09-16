# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0003_auto_20150916_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoortStuk',
            fields=[
                ('code', models.CharField(serialize=False, max_length=3, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name': 'Soort stuk',
                'verbose_name_plural': 'Soorten stukken',
            },
        ),
        migrations.CreateModel(
            name='Transactie',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('registercode', models.CharField(max_length=14)),
                ('stukdeel_1', models.CharField(null=True, max_length=5)),
                ('stukdeel_2', models.CharField(null=True, max_length=5)),
                ('stukdeel_3', models.CharField(null=True, max_length=5)),
                ('ontvangstdatum', models.DateField(null=True)),
                ('verlijdensdatum', models.DateField(null=True)),
                ('meer_kadastrale_objecten', models.BooleanField(default=False)),
                ('koopjaar', models.SmallIntegerField(null=True)),
                ('koopsom', models.IntegerField(null=True)),
                ('belastingplichtige', models.BooleanField(default=False)),
                ('soort_stuk', models.ForeignKey(null=True, to='akr.SoortStuk')),
            ],
            options={
                'verbose_name': 'Transactie',
                'verbose_name_plural': 'Transacties',
            },
        ),
    ]
