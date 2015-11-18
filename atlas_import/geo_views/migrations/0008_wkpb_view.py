# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from geo_views import migrate


class Migration(migrations.Migration):

    dependencies = [
        ('geo_views', '0007_update_views'),
    ]

    operations = [
        migrate.ManageView(view_name='geo_wkpb', sql="""
SELECT
  bk.id                                            AS id,
  bp.beperkingtype_id                              AS beperkingtype_id,
  ko.geometrie                                     AS geometrie,
  bc.omschrijving                                  AS display,
  'wkpb/beperking'                                 AS type,
  site.domain || 'wkpb/beperking/' || bp.id || '/' AS uri
FROM
  wkpb_beperkingkadastraalobject bk
  LEFT JOIN wkpb_beperking bp ON bp.id = bk.beperking_id
  LEFT JOIN lki_kadastraalobject ko ON ko.id = bk.kadastraal_object_id
  LEFT JOIN wkpb_beperkingcode bc ON bc.code = bp.beperkingtype_id
  ,
  django_site site
WHERE
  site.name = 'API Domain'
  AND bp.beperkingtype_id <> 'HS'
          """)
    ]
