# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobExecution',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('date_started', models.DateTimeField()),
                ('date_finished', models.DateTimeField(null=True)),
                ('status', models.IntegerField(default=0)),
            ],
        ),
    ]
