# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag', '0010_buurtcombinatie_gebiedsgerichtwerken_grootstedelijkproject_unesco'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GrootstedelijkProject',
            new_name='Grootstedelijkgebied',
        ),
        migrations.AlterModelOptions(
            name='grootstedelijkgebied',
            options={'verbose_name': 'Grootstedelijkgebied', 'verbose_name_plural': 'Grootstedelijke gebieden'},
        ),
        migrations.AlterField(
            model_name='bouwblok',
            name='buurt',
            field=models.ForeignKey(related_name='bouwblokken', to='bag.Buurt'),
        ),
        migrations.AlterField(
            model_name='buurt',
            name='stadsdeel',
            field=models.ForeignKey(related_name='buurten', to='bag.Stadsdeel'),
        ),
        migrations.AlterField(
            model_name='gebiedsgerichtwerken',
            name='stadsdeel',
            field=models.ForeignKey(related_name='gebiedsgerichtwerken', to='bag.Stadsdeel'),
        ),
        migrations.AlterField(
            model_name='ligplaats',
            name='buurt',
            field=models.ForeignKey(null=True, related_name='ligplaatsen', to='bag.Buurt'),
        ),
        migrations.AlterField(
            model_name='stadsdeel',
            name='gemeente',
            field=models.ForeignKey(related_name='stadsdelen', to='bag.Gemeente'),
        ),
        migrations.AlterField(
            model_name='standplaats',
            name='buurt',
            field=models.ForeignKey(null=True, related_name='standplaatsen', to='bag.Buurt'),
        ),
        migrations.AlterField(
            model_name='verblijfsobject',
            name='buurt',
            field=models.ForeignKey(null=True, related_name='verblijfsobjecten', to='bag.Buurt'),
        ),
        migrations.AlterField(
            model_name='woonplaats',
            name='gemeente',
            field=models.ForeignKey(related_name='woonplaatsen', to='bag.Gemeente'),
        ),
    ]
