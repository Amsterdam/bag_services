# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0002_auto_20150908_1131'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bron',
            options={'verbose_name_plural': 'Bronnen', 'verbose_name': 'Bron'},
        ),
        migrations.AlterModelOptions(
            name='buurt',
            options={'verbose_name_plural': 'Buurten', 'verbose_name': 'Buurt'},
        ),
        migrations.AlterModelOptions(
            name='eigendomsverhouding',
            options={'verbose_name_plural': 'Eigendomsverhoudingen', 'verbose_name': 'Eigendomsverhouding'},
        ),
        migrations.AlterModelOptions(
            name='financieringswijze',
            options={'verbose_name_plural': 'Financieringswijzes', 'verbose_name': 'Financieringswijze'},
        ),
        migrations.AlterModelOptions(
            name='gebruik',
            options={'verbose_name_plural': 'Gebruik', 'verbose_name': 'Gebruik'},
        ),
        migrations.AlterModelOptions(
            name='gemeente',
            options={'verbose_name_plural': 'Gemeentes', 'verbose_name': 'Gemeente'},
        ),
        migrations.AlterModelOptions(
            name='ligging',
            options={'verbose_name_plural': 'Ligging', 'verbose_name': 'Ligging'},
        ),
        migrations.AlterModelOptions(
            name='ligplaats',
            options={'verbose_name_plural': 'Ligplaatsen', 'verbose_name': 'Ligplaats'},
        ),
        migrations.AlterModelOptions(
            name='locatieingang',
            options={'verbose_name_plural': 'Locaties Ingang', 'verbose_name': 'Locatie Ingang'},
        ),
        migrations.AlterModelOptions(
            name='nummeraanduiding',
            options={'verbose_name_plural': 'Nummeraanduidingen', 'verbose_name': 'Nummeraanduiding'},
        ),
        migrations.AlterModelOptions(
            name='openbareruimte',
            options={'verbose_name_plural': 'Openbare Ruimtes', 'verbose_name': 'Openbare Ruimte'},
        ),
        migrations.AlterModelOptions(
            name='pand',
            options={'verbose_name_plural': 'Panden', 'verbose_name': 'Pand'},
        ),
        migrations.AlterModelOptions(
            name='redenafvoer',
            options={'verbose_name_plural': 'Reden Afvoer', 'verbose_name': 'Reden Afvoer'},
        ),
        migrations.AlterModelOptions(
            name='stadsdeel',
            options={'verbose_name_plural': 'Stadsdelen', 'verbose_name': 'Stadsdeel'},
        ),
        migrations.AlterModelOptions(
            name='standplaats',
            options={'verbose_name_plural': 'Standplaatsen', 'verbose_name': 'Standplaats'},
        ),
        migrations.AlterModelOptions(
            name='status',
            options={'verbose_name_plural': 'Status', 'verbose_name': 'Status'},
        ),
        migrations.AlterModelOptions(
            name='toegang',
            options={'verbose_name_plural': 'Toegang', 'verbose_name': 'Toegang'},
        ),
        migrations.AlterModelOptions(
            name='verblijfsobject',
            options={'verbose_name_plural': 'Verblijfsobjecten', 'verbose_name': 'Verblijfsobject'},
        ),
        migrations.AlterModelOptions(
            name='verblijfsobjectpandrelatie',
            options={'verbose_name_plural': 'Verblijfsobject-Pand relaties', 'verbose_name': 'Verblijfsobject-Pand relatie'},
        ),
        migrations.AlterModelOptions(
            name='woonplaats',
            options={'verbose_name_plural': 'Woonplaatsen', 'verbose_name': 'Woonplaats'},
        ),
    ]
