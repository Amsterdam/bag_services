# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0007_auto_20151214_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalobject',
            name='cultuurcode_bebouwd',
            field=models.ForeignKey(to='brk.CultuurCodeBebouwd', null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalobject',
            name='cultuurcode_onbebouwd',
            field=models.ForeignKey(to='brk.CultuurCodeOnbebouwd', null=True),
        ),
        migrations.AlterField(
            model_name='kadastraalobject',
            name='toestandsdatum',
            field=models.DateField(null=True),
        ),
    ]
