# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0007_auto_20150917_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='KadastraalObjectVerblijfsobject',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('vbo_id', models.CharField(max_length=14)),
                ('kadastraal_object', models.ForeignKey(related_name='verblijfsobjecten', to='akr.KadastraalObject')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
