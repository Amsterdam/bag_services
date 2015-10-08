# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


ALTER_HUISNUMMER = """ALTER TABLE bag_nummeraanduiding ALTER COLUMN huisnummer TYPE integer USING ( huisnummer::integer );"""


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0006_auto_20150929_1611'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nummeraanduiding',
            options={'verbose_name': 'Nummeraanduiding', 'ordering': ('openbare_ruimte__naam', 'huisnummer', 'huisletter', 'huisnummer_toevoeging'), 'verbose_name_plural': 'Nummeraanduidingen'},
        ),
        migrations.RunSQL(
            ALTER_HUISNUMMER, None, [
                migrations.AlterField(
                    model_name='nummeraanduiding',
                    name='huisnummer',
                    field=models.IntegerField(max_length=5),
                ),
            ]
        )
    ]
