# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brk', '0021_auto_20151221_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aanduidingnaam',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='aardaantekening',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='aardzakelijkrecht',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='appartementsrechtssplitstype',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='beschikkingsbevoegdheid',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='cultuurcodebebouwd',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='cultuurcodeonbebouwd',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='geslacht',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='land',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='rechtsvorm',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='soortgrootte',
            name='date_modified',
        ),
    ]
