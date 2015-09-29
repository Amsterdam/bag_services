# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0005_remove_verblijfsobject_kadastrale_objecten'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nummeraanduiding',
            name='openbare_ruimte',
            field=models.ForeignKey(related_name='adressen', to='bag.OpenbareRuimte'),
        ),
    ]
