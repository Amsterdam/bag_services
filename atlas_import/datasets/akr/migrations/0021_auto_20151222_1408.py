# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('akr', '0020_marker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adres',
            name='land',
        ),
        migrations.RemoveField(
            model_name='kadastraalobject',
            name='bebouwingscode',
        ),
        migrations.RemoveField(
            model_name='kadastraalobject',
            name='soort_cultuur_onbebouwd',
        ),
        migrations.RemoveField(
            model_name='kadastraalobjectverblijfsobject',
            name='kadastraal_object',
        ),
        migrations.RemoveField(
            model_name='kadastraalobjectverblijfsobject',
            name='verblijfsobject',
        ),
        migrations.RemoveField(
            model_name='kadastraalsubject',
            name='postadres',
        ),
        migrations.RemoveField(
            model_name='kadastraalsubject',
            name='soort_niet_natuurlijke_persoon',
        ),
        migrations.RemoveField(
            model_name='kadastraalsubject',
            name='titel_of_predikaat',
        ),
        migrations.RemoveField(
            model_name='kadastraalsubject',
            name='woonadres',
        ),
        migrations.RemoveField(
            model_name='transactie',
            name='soort_stuk',
        ),
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='kadastraal_object',
        ),
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='kadastraal_subject',
        ),
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='soort_recht',
        ),
        migrations.RemoveField(
            model_name='zakelijkrecht',
            name='transactie',
        ),
        migrations.DeleteModel(
            name='Adres',
        ),
        migrations.DeleteModel(
            name='Bebouwingscode',
        ),
        migrations.DeleteModel(
            name='KadastraalObject',
        ),
        migrations.DeleteModel(
            name='KadastraalObjectVerblijfsobject',
        ),
        migrations.DeleteModel(
            name='KadastraalSubject',
        ),
        migrations.DeleteModel(
            name='Land',
        ),
        migrations.DeleteModel(
            name='NietNatuurlijkePersoon',
        ),
        migrations.DeleteModel(
            name='SoortCultuurOnbebouwd',
        ),
        migrations.DeleteModel(
            name='SoortRecht',
        ),
        migrations.DeleteModel(
            name='SoortStuk',
        ),
        migrations.DeleteModel(
            name='Titel',
        ),
        migrations.DeleteModel(
            name='Transactie',
        ),
        migrations.DeleteModel(
            name='ZakelijkRecht',
        ),
    ]
