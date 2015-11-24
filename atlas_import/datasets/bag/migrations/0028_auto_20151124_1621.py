# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0027_auto_20151124_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='ligplaats',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='ligplaats',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='nummeraanduiding',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='openbareruimte',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='openbareruimte',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='openbareruimte',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='pand',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='pand',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='pand',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='standplaats',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='verblijfsobject',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='woonplaats',
            name='begin_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='woonplaats',
            name='einde_geldigheid',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='woonplaats',
            name='mutatie_gebruiker',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
