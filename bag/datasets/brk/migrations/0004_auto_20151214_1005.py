# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0003_auto_20151214_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='geboorteland',
            field=models.ForeignKey(to='brk.Land', null=True, related_name='+'),
        ),
        migrations.AlterField(
            model_name='kadastraalsubject',
            name='land_waarnaar_vertrokken',
            field=models.ForeignKey(to='brk.Land', null=True, related_name='+'),
        ),
        migrations.DeleteModel(
            name='VertrekLand',
        ),
    ]
