# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0004_auto_20160316_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buurt',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='gemeente',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='gemeente',
            name='verzorgingsgebied',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='ligplaats',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='pand',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='stadsdeel',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='standplaats',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='verblijfsobject',
            name='woningvoorraad',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='woonplaats',
            name='vervallen',
            field=models.NullBooleanField(default=None),
        ),
    ]
