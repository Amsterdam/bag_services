# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0002_ligplaats_geometrie'),
    ]

    operations = [
        migrations.AddField(
            model_name='ligplaats',
            name='document_mutatie',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='document_nummer',
            field=models.CharField(null=True, max_length=20),
        ),
    ]
