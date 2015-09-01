# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0052_replace_beperking_lkikadastraalobject_view2'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerblijfsobjectPandRelatie',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('pand', models.ForeignKey(to='atlas.Pand')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='verblijfsobject',
            name='panden',
        ),
        migrations.AddField(
            model_name='verblijfsobjectpandrelatie',
            name='verblijfsobject',
            field=models.ForeignKey(to='atlas.Verblijfsobject'),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='panden_tmp',
            field=models.ManyToManyField(through='atlas.VerblijfsobjectPandRelatie', related_name='verblijfsobjecten', to='atlas.Pand'),
        ),
    ]
