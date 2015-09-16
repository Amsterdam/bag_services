# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0002_auto_20150916_1158'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BebouwingscodeDomein',
            new_name='Bebouwingscode',
        ),
        migrations.RenameModel(
            old_name='SoortCultuurOnbebouwdDomein',
            new_name='SoortCultuurOnbebouwd',
        ),
        migrations.AlterModelOptions(
            name='bebouwingscode',
            options={'verbose_name_plural': 'Bebouwingscodes', 'verbose_name': 'Bebouwingscode'},
        ),
        migrations.AlterModelOptions(
            name='soortcultuuronbebouwd',
            options={'verbose_name_plural': 'Soorten cultuur onbebouwd', 'verbose_name': 'Soort cultuur onbebouwd'},
        ),
        migrations.RenameField(
            model_name='kadastraalobject',
            old_name='bebouwingscode_domein',
            new_name='bebouwingscode',
        ),
        migrations.RenameField(
            model_name='kadastraalobject',
            old_name='gemeentecode_domein',
            new_name='gemeentecode',
        ),
        migrations.RenameField(
            model_name='kadastraalobject',
            old_name='soort_cultuur_onbebouwd_domein',
            new_name='soort_cultuur_onbebouwd',
        ),
    ]
