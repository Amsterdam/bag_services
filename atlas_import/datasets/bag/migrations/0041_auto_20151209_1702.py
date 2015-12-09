# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0040_auto_20151209_1637'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='verblijfsobject',
            index_together=set([('_openbare_ruimte_naam', '_huisnummer', '_huisletter', '_huisnummer_toevoeging')]),
        ),
    ]
