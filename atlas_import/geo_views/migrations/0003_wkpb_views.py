# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0002_lki_views'),
        ('wkpb', '0001_initial'),
    ]

    operations = [
        migrate.ManageView(view_name='geo_wkpb', sql="""
SELECT
  bk.id               AS id,
  bp.beperkingtype_id AS beperkingtype_id,
  ko.geometrie        AS geometrie
FROM
  wkpb_beperkingkadastraalobject bk
  LEFT JOIN wkpb_beperking bp ON bp.id = bk.beperking_id
  LEFT JOIN lki_kadastraalobject ko ON ko.id = bk.kadastraal_object_id
WHERE
  bp.beperkingtype_id <> 'HS'
        """)
    ]
