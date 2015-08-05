# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0027_wkpbbrondocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wkpbbrondocument',
            name='bron',
            field=models.ForeignKey(null=True, to='atlas.WkpbBroncode'),
        ),
    ]
