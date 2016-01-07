# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lki', '0002_auto_20150908_1255'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Gemeente',
        ),
        migrations.DeleteModel(
            name='KadastraalObject',
        ),
        migrations.DeleteModel(
            name='KadastraleGemeente',
        ),
        migrations.DeleteModel(
            name='Sectie',
        ),
    ]
