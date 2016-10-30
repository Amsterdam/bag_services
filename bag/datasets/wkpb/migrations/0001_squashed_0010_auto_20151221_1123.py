# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [('wkpb', '0001_initial'), (
    'wkpb', '0002_beperkingkadastraalobject_kadastraal_object_akr'),
                ('wkpb', '0003_auto_20151020_1153'),
                ('wkpb', '0003_auto_20151020_1106'), ('wkpb', '0004_merge'),
                ('wkpb', '0005_auto_20151021_1107'),
                ('wkpb', '0006_brondocument_beperking'),
                ('wkpb', '0007_auto_20151104_1203'),
                ('wkpb', '0008_auto_20151207_1533'),
                ('wkpb', '0009_auto_20151209_1340'),
                ('wkpb', '0010_auto_20151221_1123')]

    dependencies = [
        ('brk', '0024_auto_20151221_1615'),
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
                ('code', models.CharField(serialize=False, max_length=4,
                                          primary_key=True)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
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
                ('id', models.CharField(serialize=False, max_length=33,
                                        primary_key=True)),
                ('beperking', models.ForeignKey(to='wkpb.Beperking')),
                ('kadastraal_object',
                 models.ForeignKey(to='brk.KadastraalObject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Broncode',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, max_length=4,
                                          primary_key=True)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
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
                ('inschrijfnummer', models.IntegerField()),
                ('documentnaam', models.CharField(max_length=21)),
                ('persoonsgegevens_afschermen', models.BooleanField()),
                ('soort_besluit', models.CharField(null=True, max_length=60)),
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
        migrations.AddField(
            model_name='beperking',
            name='kadastrale_objecten',
            field=models.ManyToManyField(
                through='wkpb.BeperkingKadastraalObject',
                related_name='beperkingen', to='brk.KadastraalObject'),
        ),
        migrations.AddField(
            model_name='brondocument',
            name='beperking',
            field=models.ForeignKey(null=True, to='wkpb.Beperking',
                                    related_name='documenten'),
        ),
        migrations.AlterField(
            model_name='brondocument',
            name='bron',
            field=models.ForeignKey(null=True, to='wkpb.Broncode',
                                    related_name='documenten'),
        ),
    ]
