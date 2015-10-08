# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0007_auto_20151008_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='huisnummer',
            field=models.IntegerField(),
        ),
    ]
