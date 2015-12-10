# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wkpb', '0008_auto_20151207_1533'),
    ]

    operations = [
        migrations.RenameField(
            model_name='brondocument',
            old_name='persoonsgegeven_afschermen',
            new_name='persoonsgegevens_afschermen',
        ),
    ]
