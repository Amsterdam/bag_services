# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0055_auto_20150901_1145'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerblijfsobjectNevenadresRelatie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('nummeraanduiding', models.ForeignKey(to='atlas.Nummeraanduiding')),
                ('verblijfsobject', models.ForeignKey(to='atlas.Verblijfsobject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='nevenadressen',
            field=models.ManyToManyField(to='atlas.Nummeraanduiding', through='atlas.VerblijfsobjectNevenadresRelatie'),
        ),
    ]
