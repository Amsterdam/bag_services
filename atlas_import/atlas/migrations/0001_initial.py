# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bron',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Buurt',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('vervallen', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gemeente',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('code', models.CharField(max_length=4, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('verzorgingsgebied', models.BooleanField(default=False)),
                ('vervallen', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ligplaats',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('identificatie', models.CharField(max_length=14, unique=True)),
                ('vervallen', models.BooleanField(default=False)),
                ('bron', models.ForeignKey(null=True, to='atlas.Bron')),
                ('buurt', models.ForeignKey(null=True, to='atlas.Buurt')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stadsdeel',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(serialize=False, max_length=14, primary_key=True)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('naam', models.CharField(max_length=40)),
                ('vervallen', models.BooleanField(default=False)),
                ('gemeente', models.ForeignKey(to='atlas.Gemeente')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(serialize=False, max_length=4, primary_key=True)),
                ('omschrijving', models.CharField(null=True, max_length=150)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='status',
            field=models.ForeignKey(null=True, to='atlas.Status'),
        ),
        migrations.AddField(
            model_name='buurt',
            name='stadsdeel',
            field=models.ForeignKey(to='atlas.Stadsdeel'),
        ),
    ]
