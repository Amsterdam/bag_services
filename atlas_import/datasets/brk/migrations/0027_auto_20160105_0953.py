# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0026_auto_20160104_1629'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='kadastraalobject',
            options={'ordering': ('kadastrale_gemeente__id', 'sectie', 'perceelnummer', '-index_letter', 'index_nummer')},
        ),
    ]
