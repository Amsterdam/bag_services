# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0004_woonplaats'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenbareRuimte',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('document_mutatie', models.DateField(null=True)),
                ('document_nummer', models.CharField(max_length=20, null=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('type', models.CharField(max_length=2, null=True)),
                ('naam', models.CharField(max_length=150)),
                ('code', models.CharField(max_length=5, unique=True)),
                ('straat_nummer', models.CharField(max_length=10, null=True)),
                ('naam_nen', models.CharField(max_length=24)),
                ('naam_ptt', models.CharField(max_length=17)),
                ('vervallen', models.BooleanField(default=False)),
                ('bron', models.ForeignKey(to='atlas.Bron', null=True)),
                ('status', models.ForeignKey(to='atlas.Status', null=True)),
                ('woonplaats', models.ForeignKey(to='atlas.Woonplaats')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
