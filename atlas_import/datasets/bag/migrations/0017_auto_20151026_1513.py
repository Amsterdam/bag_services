# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0016_auto_20151026_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='stadsdeel',
            name='brondocument_datum',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='stadsdeel',
            name='brondocument_naam',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='stadsdeel',
            name='ingang_cyclus',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='buurt',
            name='brondocument_naam',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='buurtcombinatie',
            name='brondocument_naam',
            field=models.CharField(null=True, max_length=100),
        ),
    ]
