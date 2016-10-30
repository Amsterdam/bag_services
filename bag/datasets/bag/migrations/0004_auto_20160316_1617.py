# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0003_auto_20160203_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='RedenOpvoer',
            fields=[
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=4, serialize=False, primary_key=True)),
                ('omschrijving', models.CharField(max_length=150, null=True)),
            ],
            options={
                'verbose_name': 'Reden Opvoer',
                'verbose_name_plural': 'Reden Opvoer',
            },
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='reden_opvoer',
            field=models.ForeignKey(to='bag.RedenOpvoer', null=True),
        ),
    ]
