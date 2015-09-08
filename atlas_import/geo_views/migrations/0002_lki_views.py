# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from geo_views import migrate


class Migration(migrations.Migration):

    dependencies = [
        ('geo_views', '0001_bag_views'),
        ('lki', '0002_auto_20150908_1255'),
    ]

    operations = [
        migrate.ManageView(view_name='geo_lki_gemeente',
                           sql='SELECT id,gemeentenaam,geometrie FROM lki_gemeente'),
        migrate.ManageView(view_name='geo_lki_kadastralegemeente',
                           sql='SELECT id,code,geometrie FROM lki_kadastralegemeente'),
        migrate.ManageView(view_name='geo_lki_sectie',
                           sql='SELECT id,code,geometrie FROM lki_sectie'),
        migrate.ManageView(view_name='geo_lki_kadastraalobject',
                           sql='SELECT id,perceelnummer,geometrie FROM lki_kadastraalobject'),
    ]
