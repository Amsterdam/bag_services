# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0033_beperking_datum_in_werking'),
    ]

    operations = [
        migrations.AddField(
            model_name='beperking',
            name='datum_einde',
            field=models.DateField(null=True),
        ),
    ]
