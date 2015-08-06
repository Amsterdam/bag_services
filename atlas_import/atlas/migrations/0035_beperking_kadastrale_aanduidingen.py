# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0034_beperking_datum_einde'),
    ]

    operations = [
        migrations.AddField(
            model_name='beperking',
            name='kadastrale_aanduidingen',
            field=django.contrib.postgres.fields.ArrayField(size=None, default=[], base_field=models.CharField(max_length=17)),
        ),
    ]
