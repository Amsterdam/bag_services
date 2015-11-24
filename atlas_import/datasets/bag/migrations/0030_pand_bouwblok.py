# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0029_verblijfsobject_verhuurbare_eenheden'),
    ]

    operations = [
        migrations.AddField(
            model_name='pand',
            name='bouwblok',
            field=models.ForeignKey(null=True, to='bag.Bouwblok'),
        ),
    ]
