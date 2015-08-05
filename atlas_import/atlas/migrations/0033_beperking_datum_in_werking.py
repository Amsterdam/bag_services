# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0032_auto_20150805_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='beperking',
            name='datum_in_werking',
            field=models.DateField(default=datetime.datetime(2015, 8, 5, 15, 27, 17, 133940, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
