# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0019_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kadastraalsubject',
            options={'verbose_name': 'Kadastraal subject',
                     'verbose_name_plural': 'Kadastrale subjecten',
                     'permissions': (('view_sensitive_details',
                                      'Kan privacy-gevoelige data inzien'),)},
        ),
    ]
