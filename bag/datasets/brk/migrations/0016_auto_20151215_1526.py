# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0015_auto_20151215_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='zakelijkrecht',
            name='zrt_id',
            field=models.CharField(default='x', max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='zakelijkrecht',
            name='betrokken_bij',
            field=models.ForeignKey(related_name='betrokken_bij_set', null=True, to='brk.KadastraalSubject'),
        ),
        migrations.AlterField(
            model_name='zakelijkrecht',
            name='ontstaan_uit',
            field=models.ForeignKey(related_name='ontstaan_uit_set', null=True, to='brk.KadastraalSubject'),
        ),
    ]
