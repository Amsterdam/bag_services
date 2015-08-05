# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0026_wkpbbroncode'),
    ]

    operations = [
        migrations.CreateModel(
            name='WkpbBrondocument',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('documentnummer', models.IntegerField()),
                ('documentnaam', models.CharField(max_length=18)),
                ('persoonsgegeven_afschermen', models.BooleanField()),
                ('soort_besluit', models.CharField(null=True, max_length=60)),
                ('bron', models.ForeignKey(to='atlas.WkpbBroncode')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
