# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0010_remove_kadastraalobject_gemeente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='belast_azt',
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='belast_azt',
            field=models.ManyToManyField(to='brk.AardZakelijkRecht',
                                         related_name='_belast_azt_+'),
        ),
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='belast_met_azt',
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='belast_met_azt',
            field=models.ManyToManyField(to='brk.AardZakelijkRecht',
                                         related_name='_belast_met_azt_+'),
        ),
    ]
