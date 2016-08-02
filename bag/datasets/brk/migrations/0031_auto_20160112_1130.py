# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0030_auto_20160111_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aperceelgperceelrelatie',
            name='id',
            field=models.CharField(max_length=121, serialize=False, primary_key=True),
        ),
    ]
