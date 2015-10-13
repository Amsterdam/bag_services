# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0014_auto_20151008_1034'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kadastraalsubject',
            options={'permissions': (('view_sensitive_details', 'Kan privacy-gevoelige data inzien'),), 'verbose_name_plural': 'Kadastrale subjecten', 'verbose_name': 'Kadastraal subject'},
        ),
    ]
