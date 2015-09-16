# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adres',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('straatnaam', models.CharField(max_length=24, null=True)),
                ('huisnummer', models.IntegerField(null=True)),
                ('huisletter', models.CharField(max_length=1, null=True)),
                ('toevoeging', models.CharField(max_length=4, null=True)),
                ('aanduiding', models.CharField(max_length=2, null=True)),
                ('postcode', models.CharField(max_length=6, null=True)),
                ('woonplaats', models.CharField(max_length=24, null=True)),
                ('adresregel_1', models.CharField(max_length=39, null=True)),
                ('adresregel_2', models.CharField(max_length=39, null=True)),
                ('adresregel_3', models.CharField(max_length=39, null=True)),
                ('beschrijving', models.CharField(max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='KadastraalSubject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(max_length=14, primary_key=True, serialize=False)),
                ('subjectnummer', models.BigIntegerField()),
                ('geslachtsaanduiding', models.CharField(max_length=1, choices=[('m', 'Man'), ('v', 'Vrouw'), ('a', 'Aanbieder'), ('o', 'Onbekend')], null=True, blank=True)),
                ('geslachtsnaam', models.CharField(max_length=128, null=True)),
                ('diacritisch', models.BooleanField(default=False)),
                ('naam_niet_natuurlijke_persoon', models.CharField(max_length=512, null=True)),
                ('soort_subject', models.CharField(max_length=1, choices=[('m', 'Man'), ('v', 'Vrouw'), ('a', 'Aanbieder'), ('o', 'Onbekend')], null=True)),
                ('voorletters', models.CharField(max_length=5, null=True)),
                ('voornamen', models.CharField(max_length=128, null=True)),
                ('voorvoegsel', models.CharField(max_length=10, null=True)),
                ('geboortedatum', models.DateField(null=True)),
                ('geboorteplaats', models.CharField(max_length=24, null=True)),
                ('overleden', models.BooleanField(default=False)),
                ('overlijdensdatum', models.DateField(null=True)),
                ('zetel', models.CharField(max_length=24, null=True)),
                ('a_nummer', models.BigIntegerField(null=True)),
                ('postadres', models.ForeignKey(to='akr.Adres', related_name='postadres', null=True)),
            ],
            options={
                'verbose_name_plural': 'Kadastrale subjecten',
                'verbose_name': 'Kadastraal subject',
            },
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'verbose_name_plural': 'Landen',
                'verbose_name': 'Land',
            },
        ),
        migrations.CreateModel(
            name='NietNatuurlijkePersoon',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('omschrijving', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'Soorten niet-natuurlijke persoon',
                'verbose_name': 'Soort niet-natuurlijke persoon',
            },
        ),
        migrations.CreateModel(
            name='Titel',
            fields=[
                ('code', models.CharField(max_length=11, primary_key=True, serialize=False)),
                ('omschrijving', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name_plural': 'Adelijke titels en predikaten',
                'verbose_name': 'Adelijke titel of predikaat',
            },
        ),
        migrations.AlterModelOptions(
            name='bebouwingscodedomein',
            options={'verbose_name_plural': 'Bebouwingscodes domein', 'verbose_name': 'Bebouwingscode domein'},
        ),
        migrations.AlterModelOptions(
            name='kadastraalobject',
            options={'verbose_name_plural': 'Kadastrale objecten', 'verbose_name': 'Kadastraal object'},
        ),
        migrations.AlterModelOptions(
            name='soortcultuuronbebouwddomein',
            options={'verbose_name_plural': 'Soorten cultuur onbebouwd domein', 'verbose_name': 'Soort cultuur onbebouwd domein'},
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='soort_niet_natuurlijke_persoon',
            field=models.ForeignKey(to='akr.NietNatuurlijkePersoon', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='titel_of_predikaat',
            field=models.ForeignKey(to='akr.Titel', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='woonadres',
            field=models.ForeignKey(to='akr.Adres', related_name='woonadres', null=True),
        ),
        migrations.AddField(
            model_name='adres',
            name='land',
            field=models.ForeignKey(to='akr.Land', null=True),
        ),
    ]
