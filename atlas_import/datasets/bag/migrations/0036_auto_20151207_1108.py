# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0035_auto_20151125_1610'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bouwblok',
            options={'ordering': ('code',), 'verbose_name_plural': 'Bouwblokken', 'verbose_name': 'Bouwblok'},
        ),
        migrations.AlterModelOptions(
            name='buurt',
            options={'ordering': ('vollcode',), 'verbose_name_plural': 'Buurten', 'verbose_name': 'Buurt'},
        ),
        migrations.AlterModelOptions(
            name='buurtcombinatie',
            options={'ordering': ('code',), 'verbose_name_plural': 'Buurtcombinaties', 'verbose_name': 'Buurtcombinatie'},
        ),
        migrations.AlterModelOptions(
            name='gebiedsgerichtwerken',
            options={'ordering': ('code',), 'verbose_name_plural': 'Gebiedsgerichtwerken', 'verbose_name': 'Gebiedsgerichtwerken'},
        ),
        migrations.AlterModelOptions(
            name='openbareruimte',
            options={'ordering': ('naam', 'id'), 'verbose_name_plural': 'Openbare Ruimtes', 'verbose_name': 'Openbare Ruimte'},
        ),
    ]
