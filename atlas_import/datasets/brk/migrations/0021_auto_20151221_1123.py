# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0020_auto_20151216_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobjectverblijfsobjectrelatie',
            name='id',
            field=models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4),
        ),
    ]
