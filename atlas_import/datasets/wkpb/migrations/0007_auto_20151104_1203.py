# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wkpb', '0006_brondocument_beperking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brondocument',
            name='bron',
            field=models.ForeignKey(related_name='documenten', null=True, to='wkpb.Broncode'),
        ),
    ]
