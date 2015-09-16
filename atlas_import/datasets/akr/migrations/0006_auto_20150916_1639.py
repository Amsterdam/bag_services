# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0005_soortrecht_zakelijkrecht'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='voorletters',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
