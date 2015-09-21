# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from geo_views import migrate


class Migration(migrations.Migration):

    dependencies = [
        ('geo_views', '0003_wkpb_views'),
    ]

    operations = [
        migrate.ManageView(view_name='geo_lki_gemeente',
                           sql="""SELECT id,gemeentecode,gemeentenaam,geometrie FROM lki_gemeente"""),
        migrate.ManageView(view_name='geo_lki_sectie',
                           sql="""SELECT id,kadastrale_gemeente_code || ' ' || code as volledige_code,code,geometrie FROM lki_sectie"""),
        migrate.ManageView(view_name='geo_lki_kadastraalobject',
                           sql="""SELECT id,kadastrale_gemeente_code || ' ' || sectie_code || ' ' || perceelnummer as volledige_code, perceelnummer,geometrie FROM lki_kadastraalobject"""),
    ]
