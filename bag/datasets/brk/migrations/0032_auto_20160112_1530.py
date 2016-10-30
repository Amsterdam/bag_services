# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bag', '0001_squashed_0042_auto_20151210_0952'),
        ('brk', '0031_auto_20160112_1130'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZakelijkRechtVerblijfsobjectRelatie',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False,
                                        verbose_name='ID', primary_key=True)),
                (
                'verblijfsobject', models.ForeignKey(to='bag.Verblijfsobject')),
                ('zakelijk_recht', models.ForeignKey(to='brk.ZakelijkRecht')),
            ],
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='verblijfsobjecten',
            field=models.ManyToManyField(to='bag.Verblijfsobject',
                                         through='brk.ZakelijkRechtVerblijfsobjectRelatie',
                                         related_name='rechten'),
        ),
    ]
