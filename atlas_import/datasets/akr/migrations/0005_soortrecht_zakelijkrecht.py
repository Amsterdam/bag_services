# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0004_soortstuk_transactie'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoortRecht',
            fields=[
                ('code', models.CharField(max_length=6, serialize=False, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name': 'Soort recht',
                'verbose_name_plural': 'Soorten recht',
            },
        ),
        migrations.CreateModel(
            name='ZakelijkRecht',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('identificatie', models.CharField(max_length=14)),
                ('volgnummer', models.IntegerField(null=True)),
                ('aandeel_medegerechtigden', models.CharField(null=True, max_length=16)),
                ('aandeel_subject', models.CharField(null=True, max_length=16)),
                ('einde_filiatie', models.BooleanField(default=False)),
                ('sluimerend', models.BooleanField(default=False)),
                ('kadastraal_object', models.ForeignKey(to='akr.KadastraalObject')),
                ('kadastraal_subject', models.ForeignKey(to='akr.KadastraalSubject')),
                ('soort_recht', models.ForeignKey(null=True, to='akr.SoortRecht')),
                ('transactie', models.ForeignKey(to='akr.Transactie')),
            ],
            options={
                'verbose_name': 'Zakelijke recht',
                'verbose_name_plural': 'Zakelijke rechten',
            },
        ),
    ]
