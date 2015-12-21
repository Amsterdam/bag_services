# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0023_auto_20151221_1521'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='kadastraalsubject',
            index_together=set([('naam', 'statutaire_naam')]),
        ),
    ]
