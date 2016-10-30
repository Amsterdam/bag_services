# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0025_remove_kadastraalobject_g_percelen'),
    ]

    operations = [
        migrations.CreateModel(
            name='APerceelGPerceelRelatie',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, default=uuid.uuid4)),
                ('a_perceel', models.ForeignKey(to='brk.KadastraalObject', related_name='g_perceel_relaties')),
                ('g_perceel', models.ForeignKey(to='brk.KadastraalObject', related_name='a_perceel_relaties')),
            ],
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='g_percelen',
            field=models.ManyToManyField(related_name='a_percelen', to='brk.KadastraalObject', through='brk.APerceelGPerceelRelatie'),
        ),
    ]
