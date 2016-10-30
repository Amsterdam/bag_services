# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0028_kadastralegemeente_naam'),
    ]

    operations = [
        migrations.AddField(
            model_name='zakelijkrecht',
            name='_kadastraal_object_aanduiding',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='_kadastraal_subject_naam',
            field=models.CharField(max_length=200, default=''),
            preserve_default=False,
        ),
    ]
