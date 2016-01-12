# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        # ('bag', '0003_auto_20150908_1255'),
        ('akr', '0008_kadastraalobjectverblijfsobject'),
    ]

    operations = [
        migrations.AddField(
            model_name='kadastraalobjectverblijfsobject',
            name='verblijfsobject',
            field=models.ForeignKey(to='bag.Verblijfsobject', null=True),
        ),
        migrations.AlterField(
            model_name='zakelijkrecht',
            name='kadastraal_object',
            field=models.ForeignKey(related_name='rechten', to='akr.KadastraalObject'),
        ),
        migrations.AlterField(
            model_name='zakelijkrecht',
            name='kadastraal_subject',
            field=models.ForeignKey(related_name='rechten', to='akr.KadastraalSubject'),
        ),
        migrations.AlterField(
            model_name='zakelijkrecht',
            name='transactie',
            field=models.ForeignKey(related_name='rechten', to='akr.Transactie'),
        ),
    ]
