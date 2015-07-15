# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskExecution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('date_started', models.DateTimeField(null=True)),
                ('date_finished', models.DateTimeField(null=True)),
                ('status', models.IntegerField(choices=[(0, 'Started'), (1, 'Finished'), (2, 'Failed')], default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='jobexecution',
            name='date_started',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='jobexecution',
            name='status',
            field=models.IntegerField(choices=[(0, 'Running'), (1, 'Finished'), (2, 'Failed')], default=0),
        ),
        migrations.AddField(
            model_name='taskexecution',
            name='job',
            field=models.ForeignKey(to='batch.JobExecution'),
        ),
    ]
