# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('wkpb', '0002_auto_20160112_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brondocument',
            name='persoonsgegevens_afschermen',
            field=models.NullBooleanField(),
        ),
    ]
