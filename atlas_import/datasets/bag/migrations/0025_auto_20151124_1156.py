# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0024_openbareruimte_landelijk_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pand',
            old_name='identificatie',
            new_name='landelijk_id',
        ),
    ]
