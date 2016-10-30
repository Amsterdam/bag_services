# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('brk', '0035_auto_20160408_1705'),
        ('geo_views', '0002_display_subtype'),
    ]

    operations = [
        migrate.ManageView(view_name='geo_lki_kadastraalobject', sql="""
SELECT
  ko.id                                                     AS id,
  ko.aanduiding                                             AS volledige_code,
  ko.perceelnummer                                          AS perceelnummer,
  coalesce(ko.point_geom, ko.poly_geom)                     AS geometrie,
  ko.aanduiding                                             AS display,
  'kadaster/kadastraal_object'                              AS type,
  site.domain || 'brk/object/' || ko.id || '/' AS uri
FROM brk_kadastraalobject ko, django_site site
WHERE site.name = 'API Domain'
"""),
        migrate.ManageView(view_name='geo_wkpb', sql="""
SELECT
  bk.id                                            AS id,
  bp.beperkingtype_id                              AS beperkingtype_id,
  coalesce(ko.point_geom, ko.poly_geom)            AS geometrie,
  bc.omschrijving                                  AS display,
  'wkpb/beperking'                                 AS type,
  site.domain || 'wkpb/beperking/' || bp.id || '/' AS uri
FROM
  wkpb_beperkingkadastraalobject bk
  LEFT JOIN wkpb_beperking bp ON bp.id = bk.beperking_id
  LEFT JOIN brk_kadastraalobject ko ON ko.id = bk.kadastraal_object_id
  LEFT JOIN wkpb_beperkingcode bc ON bc.code = bp.beperkingtype_id
  ,
  django_site site
WHERE
  site.name = 'API Domain'
  AND bp.beperkingtype_id <> 'HS'
          """,
                           ),
    ]
