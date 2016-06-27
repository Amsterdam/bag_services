# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0032_auto_20160112_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='meer_objecten',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='kadastraalobject',
            name='voorlopige_kadastrale_grens',
            field=models.NullBooleanField(default=None),
        ),
    ]
