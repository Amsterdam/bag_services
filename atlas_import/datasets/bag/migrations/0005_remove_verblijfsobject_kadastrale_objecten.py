# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0004_verblijfsobject_kadastrale_objecten'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verblijfsobject',
            name='kadastrale_objecten',
        ),
    ]
