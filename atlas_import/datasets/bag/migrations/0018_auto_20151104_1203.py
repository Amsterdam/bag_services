# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0017_auto_20151026_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bouwblok',
            name='buurt',
            field=models.ForeignKey(related_name='bouwblokken', null=True, to='bag.Buurt'),
        ),
        migrations.AlterField(
            model_name='openbareruimte',
            name='woonplaats',
            field=models.ForeignKey(related_name='openbare_ruimtes', to='bag.Woonplaats'),
        ),
    ]
