# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0016_auto_20151215_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stukdeel',
            name='aantekening',
        ),
        migrations.RemoveField(
            model_name='stukdeel',
            name='aard_stukdeel',
        ),
        migrations.RemoveField(
            model_name='stukdeel',
            name='register_code',
        ),
        migrations.RemoveField(
            model_name='stukdeel',
            name='soort_register',
        ),
        migrations.RemoveField(
            model_name='stukdeel',
            name='tenaamstelling',
        ),
        migrations.RenameField(
            model_name='aantekening',
            old_name='kadastraal_subject',
            new_name='opgelegd_door',
        ),
        migrations.RemoveField(
            model_name='aantekening',
            name='type',
        ),
        migrations.RemoveField(
            model_name='aantekening',
            name='zekerheidsrecht',
        ),
        migrations.RemoveField(
            model_name='kadastraalobject',
            name='g_perceel',
        ),
        migrations.RemoveField(
            model_name='kadastraalsubject',
            name='bsn',
        ),
        migrations.AddField(
            model_name='kadastraalobject',
            name='g_percelen',
            field=models.ManyToManyField(related_name='a_percelen', to='brk.KadastraalObject'),
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='noemer',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='zakelijkrecht',
            name='teller',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='AardStukdeel',
        ),
        migrations.DeleteModel(
            name='RegisterCode',
        ),
        migrations.DeleteModel(
            name='SoortRegister',
        ),
        migrations.DeleteModel(
            name='Stukdeel',
        ),
    ]
