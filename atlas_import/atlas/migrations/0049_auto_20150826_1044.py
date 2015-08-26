# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0048_add_beperking_lkikadastraalobject_view2'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeperkingKadastraalObject',
            fields=[
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(primary_key=True, serialize=False, max_length=33)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='beperking',
            name='kadastrale_aanduidingen',
        ),
        migrations.AddField(
            model_name='beperkingkadastraalobject',
            name='beperking',
            field=models.ForeignKey(to='atlas.Beperking'),
        ),
        migrations.AddField(
            model_name='beperkingkadastraalobject',
            name='kadastraal_object',
            field=models.ForeignKey(to='atlas.LkiKadastraalObject'),
        ),
    ]
