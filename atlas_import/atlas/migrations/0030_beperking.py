# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0029_auto_20150805_1609'),
    ]

    operations = [
        migrations.CreateModel(
            name='Beperking',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('inschrijfnummer', models.IntegerField()),
                ('datum_in_werking', models.DateField()),
                ('datum_einde', models.DateField(null=True)),
                ('beperkingcode', models.ForeignKey(to='atlas.Beperkingcode')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
