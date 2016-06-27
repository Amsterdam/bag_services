# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0033_auto_20160321_1122'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='zakelijkrecht',
            index_together=set([('aard_zakelijk_recht', '_kadastraal_subject_naam')]),
        ),
    ]
