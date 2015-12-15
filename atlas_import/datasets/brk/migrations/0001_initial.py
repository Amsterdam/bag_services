# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0042_auto_20151210_0952'),
    ]

    operations = [
        migrations.CreateModel(
            name='AanduidingNaam',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Aantekening',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=60)),
                ('omschrijving', models.TextField()),
                ('type', models.CharField(max_length=33)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AardAantekening',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AardStukdeel',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AardZakelijkRecht',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Adres',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, max_length=32)),
                ('openbareruimte_naam', models.CharField(null=True, max_length=80)),
                ('huisnummer', models.IntegerField(null=True)),
                ('huisletter', models.CharField(null=True, max_length=1)),
                ('toevoeging', models.CharField(null=True, max_length=4)),
                ('postcode', models.CharField(null=True, max_length=6)),
                ('woonplaats', models.CharField(null=True, max_length=80)),
                ('postbus_nummer', models.IntegerField(null=True)),
                ('postbus_postcode', models.CharField(null=True, max_length=50)),
                ('postbus_woonplaats', models.CharField(null=True, max_length=80)),
                ('buitenland_adres', models.CharField(null=True, max_length=100)),
                ('buitenland_woonplaats', models.CharField(null=True, max_length=100)),
                ('buitenland_regio', models.CharField(null=True, max_length=100)),
                ('buitenland_naam', models.CharField(null=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AppartementsrechtsSplitsType',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Beschikkingsbevoegdheid',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CultuurCodeBebouwd',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CultuurCodeOnbebouwd',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gemeente',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('gemeente', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
            ],
            options={
                'verbose_name_plural': 'Gemeentes',
                'verbose_name': 'Gemeente',
            },
        ),
        migrations.CreateModel(
            name='Geslacht',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraalObject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=60)),
                ('aanduiding', models.CharField(max_length=16)),
                ('perceelnummer', models.IntegerField()),
                ('index_letter', models.CharField(max_length=1)),
                ('index_nummer', models.IntegerField()),
                ('grootte', models.IntegerField()),
                ('koopsom', models.IntegerField(null=True)),
                ('koopsom_valuta_code', models.CharField(null=True, max_length=50)),
                ('koopjaar', models.CharField(null=True, max_length=15)),
                ('meer_objecten', models.BooleanField(default=False)),
                ('register9_tekst', models.TextField()),
                ('status_code', models.CharField(max_length=50)),
                ('toestandsdatum', models.DateField()),
                ('voorlopige_kadastrale_grens', models.BooleanField(default=False)),
                ('in_onderzoek', models.TextField(null=True)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=28992)),
                ('cultuurcode_bebouwd', models.ForeignKey(to='brk.CultuurCodeBebouwd')),
                ('cultuurcode_onbebouwd', models.ForeignKey(to='brk.CultuurCodeOnbebouwd')),
                ('g_perceel', models.ForeignKey(to='brk.KadastraalObject', null=True, related_name='a_percelen')),
                ('gemeente', models.ForeignKey(to='brk.Gemeente', related_name='kadastrale_objecten')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraalObjectVerblijfsobjectRelatie',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('kadastraal_object', models.ForeignKey(to='brk.KadastraalObject')),
                ('verblijfsobject', models.ForeignKey(to='bag.Verblijfsobject', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraalSubject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=60)),
                ('type', models.SmallIntegerField(choices=[(0, 'Natuurlijk persoon'), (1, 'Niet-natuurlijk persoon')])),
                ('bsn', models.CharField(null=True, max_length=50)),
                ('voornamen', models.CharField(null=True, max_length=200)),
                ('voorvoegsels', models.CharField(null=True, max_length=10)),
                ('naam', models.CharField(null=True, max_length=200)),
                ('geboortedatum', models.DateField(null=True)),
                ('geboorteplaats', models.CharField(max_length=80)),
                ('overlijdensdatum', models.DateField(null=True)),
                ('partner_voornamen', models.CharField(max_length=200)),
                ('partner_voorvoegsels', models.CharField(max_length=10)),
                ('partner_naam', models.CharField(max_length=200)),
                ('rsin', models.CharField(null=True, max_length=80)),
                ('kvknummer', models.CharField(null=True, max_length=8)),
                ('statutaire_naam', models.CharField(null=True, max_length=200)),
                ('statutaire_zetel', models.CharField(null=True, max_length=24)),
                ('bron', models.SmallIntegerField(choices=[(0, 'Basisregistraties'), (1, 'Kadaster')])),
                ('aanduiding_naam', models.ForeignKey(to='brk.AanduidingNaam', null=True)),
                ('beschikkingsbevoegdheid', models.ForeignKey(to='brk.Beschikkingsbevoegdheid', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KadastraleGemeente',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=200)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
                ('gemeente', models.ForeignKey(to='brk.Gemeente', related_name='kadastrale_gemeentes')),
            ],
            options={
                'verbose_name_plural': 'Kadastrale Gemeentes',
                'verbose_name': 'Kadastrale Gemeente',
            },
        ),
        migrations.CreateModel(
            name='KadastraleSectie',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=200)),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=28992)),
                ('kadastrale_gemeente', models.ForeignKey(to='brk.KadastraleGemeente', related_name='secties')),
            ],
            options={
                'verbose_name_plural': 'Kadastrale Secties',
                'verbose_name': 'Kadastrale Sectie',
            },
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rechtsvorm',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegisterCode',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SoortGrootte',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SoortRegister',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stukdeel',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=60)),
                ('koopsom', models.IntegerField()),
                ('koopsom_valuta', models.CharField(max_length=50)),
                ('stuk_id', models.CharField(max_length=60)),
                ('portefeuille_nummer', models.CharField(max_length=16)),
                ('tijdstip_aanbieding', models.DateTimeField()),
                ('reeks_code', models.CharField(max_length=50)),
                ('volgnummer', models.IntegerField()),
                ('deel_soort', models.CharField(max_length=5)),
                ('aantekening', models.ForeignKey(to='brk.Aantekening')),
                ('aard_stukdeel', models.ForeignKey(to='brk.AardStukdeel')),
                ('register_code', models.ForeignKey(to='brk.RegisterCode')),
                ('soort_register', models.ForeignKey(to='brk.SoortRegister')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VertrekLand',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('omschrijving', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ZakelijkRecht',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=60)),
                ('aard_zakelijk_recht_akr', models.CharField(null=True, max_length=3)),
                ('belast_azt', models.CharField(max_length=15)),
                ('belast_met_azt', models.CharField(max_length=15)),
                ('beperkt_tot_tng', models.BooleanField(default=False)),
                ('kadastraal_object_status', models.CharField(max_length=50)),
                ('aard_zakelijk_recht', models.ForeignKey(to='brk.AardZakelijkRecht', null=True)),
                ('app_rechtsplitstype', models.ForeignKey(to='brk.AppartementsrechtsSplitsType', null=True)),
                ('betrokken_bij', models.ForeignKey(to='brk.ZakelijkRecht', null=True, related_name='betrokken_bij_set')),
                ('kadastraal_object', models.ForeignKey(to='brk.KadastraalObject', related_name='rechten')),
                ('kadastraal_subject', models.ForeignKey(to='brk.KadastraalSubject', related_name='rechten')),
                ('ontstaan_uit', models.ForeignKey(to='brk.ZakelijkRecht', null=True, related_name='ontstaan_uit_set')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='stukdeel',
            name='tenaamstelling',
            field=models.ForeignKey(to='brk.ZakelijkRecht'),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='geboorteland',
            field=models.ForeignKey(to='brk.Land', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='geslacht',
            field=models.ForeignKey(to='brk.Geslacht', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='land_waarnaar_vertrokken',
            field=models.ForeignKey(to='brk.VertrekLand', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='postadres',
            field=models.ForeignKey(to='brk.Adres', null=True, related_name='postadres'),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='rechtsvorm',
            field=models.ForeignKey(to='brk.Rechtsvorm', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalsubject',
            name='woonadres',
            field=models.ForeignKey(to='brk.Adres', null=True, related_name='woonadres'),
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='kadastrale_gemeente',
            field=models.ForeignKey(to='brk.KadastraleGemeente', related_name='kadastrale_objecten'),
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='sectie',
            field=models.ForeignKey(to='brk.KadastraleSectie', related_name='kadastrale_objecten'),
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='soort_grootte',
            field=models.ForeignKey(to='brk.SoortGrootte', null=True),
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='verblijfsobjecten',
            field=models.ManyToManyField(to='bag.Verblijfsobject', through='brk.KadastraalObjectVerblijfsobjectRelatie'),
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='voornaamste_gerechtigde',
            field=models.ForeignKey(to='brk.KadastraalSubject'),
        ),
        migrations.AddField(
            model_name='adres',
            name='buitenland_land',
            field=models.ForeignKey(to='brk.Land', null=True),
        ),
        migrations.AddField(
            model_name='aantekening',
            name='aard_aantekening',
            field=models.ForeignKey(to='brk.AardAantekening'),
        ),
        migrations.AddField(
            model_name='aantekening',
            name='kadastraal_object',
            field=models.ForeignKey(to='brk.KadastraalObject', null=True, related_name='aantekeningen'),
        ),
        migrations.AddField(
            model_name='aantekening',
            name='kadastraal_subject',
            field=models.ForeignKey(to='brk.KadastraalSubject', null=True, related_name='aantekeningen'),
        ),
        migrations.AddField(
            model_name='aantekening',
            name='zekerheidsrecht',
            field=models.ForeignKey(to='brk.ZakelijkRecht', null=True, related_name='aantekeningen'),
        ),
    ]
