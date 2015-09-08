# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lki', '0002_auto_20150908_1255'),
    ]

    operations = [
        migrations.CreateModel(
            name='Beperking',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('inschrijfnummer', models.IntegerField()),
                ('datum_in_werking', models.DateField()),
                ('datum_einde', models.DateField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Beperkingen',
                'verbose_name': 'Beperking',
            },
        ),
        migrations.CreateModel(
            name='Beperkingcode',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'verbose_name_plural': 'Beperkingcodes',
                'verbose_name': 'Beperkingcode',
            },
        ),
        migrations.CreateModel(
            name='BeperkingKadastraalObject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=33, primary_key=True)),
                ('beperking', models.ForeignKey(to='wkpb.Beperking')),
                ('kadastraal_object', models.ForeignKey(to='lki.KadastraalObject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Broncode',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'verbose_name_plural': 'Broncodes',
                'verbose_name': 'Broncode',
            },
        ),
        migrations.CreateModel(
            name='Brondocument',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('documentnummer', models.IntegerField()),
                ('documentnaam', models.CharField(max_length=21)),
                ('persoonsgegeven_afschermen', models.BooleanField()),
                ('soort_besluit', models.CharField(max_length=60, null=True)),
                ('bron', models.ForeignKey(null=True, to='wkpb.Broncode')),
            ],
            options={
                'verbose_name_plural': 'Brondocumenten',
                'verbose_name': 'Brondocument',
            },
        ),
        migrations.AddField(
            model_name='beperking',
            name='beperkingtype',
            field=models.ForeignKey(to='wkpb.Beperkingcode'),
        ),
    ]
