# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bag', '0001_squashed_0042_auto_20151210_0952'),
        ('wkpb', '0001_squashed_0010_auto_20151221_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeperkingVerblijfsobject',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True,
                                        serialize=False, verbose_name='ID')),
                ('beperking', models.ForeignKey(to='wkpb.Beperking')),
                (
                'verblijfsobject', models.ForeignKey(to='bag.Verblijfsobject')),
            ],
        ),
        migrations.AddField(
            model_name='beperking',
            name='verblijfsobjecten',
            field=models.ManyToManyField(
                through='wkpb.BeperkingVerblijfsobject',
                related_name='beperkingen', to='bag.Verblijfsobject'),
        ),
    ]
