# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wkpb', '0007_auto_20151104_1203'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brondocument',
            old_name='documentnummer',
            new_name='inschrijfnummer',
        ),
    ]
