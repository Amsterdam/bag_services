# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BebouwingscodeDomein',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='KadastraalObject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, primary_key=True, max_length=14)),
                ('gemeentecode_domein', models.CharField(max_length=5)),
                ('sectie', models.CharField(max_length=2)),
                ('perceelnummer', models.IntegerField()),
                ('objectindex_letter', models.CharField(max_length=1)),
                ('objectindex_nummer', models.IntegerField()),
                ('grootte', models.IntegerField(null=True)),
                ('grootte_geschat', models.BooleanField(default=False)),
                ('cultuur_tekst', models.CharField(null=True, max_length=65)),
                ('meer_culturen_onbebouwd', models.BooleanField(default=False)),
                ('kaartblad', models.IntegerField(null=True)),
                ('ruitletter', models.CharField(null=True, max_length=1)),
                ('ruitnummer', models.IntegerField(null=True)),
                ('omschrijving_deelperceel', models.CharField(null=True, max_length=20)),
                ('bebouwingscode_domein', models.ForeignKey(null=True, to='akr.BebouwingscodeDomein')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SoortCultuurOnbebouwdDomein',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='soort_cultuur_onbebouwd_domein',
            field=models.ForeignKey(null=True, to='akr.SoortCultuurOnbebouwdDomein'),
        ),
    ]
