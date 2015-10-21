# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wkpb', '0005_auto_20151021_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='brondocument',
            name='beperking',
            field=models.ForeignKey(related_name='documenten', to='wkpb.Beperking', null=True),
        ),
    ]
