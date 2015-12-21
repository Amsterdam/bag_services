# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0009_bag_opr_view'),
        ('brk', '0021_auto_20151221_1123'),
        ('wkpb', '0010_auto_20151221_1123'),
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
  LEFT JOIN brk_kadastraalobject ko ON ko.id = bk.kadastraal_object_id
  LEFT JOIN wkpb_beperkingcode bc ON bc.code = bp.beperkingtype_id
  ,
  django_site site
WHERE
  site.name = 'API Domain'
  AND bp.beperkingtype_id <> 'HS'
          """),

        migrate.ManageView(view_name='geo_lki_kadastraalobject', sql="""
SELECT
  ko.id                                                     AS id,
  ko.aanduiding                                             AS volledige_code,
  ko.perceelnummer                                          AS perceelnummer,
  ko.geometrie                                              AS geometrie,
  ko.aanduiding                                             AS display,
  'kadaster/kadastraal_object'                              AS type,
  site.domain || 'brk/object/' || ko.id || '/' AS uri
FROM brk_kadastraalobject ko, django_site site
WHERE site.name = 'API Domain'
"""),

        migrate.ManageView(view_name='geo_lki_gemeente',
                           sql="""
SELECT
  gemeente AS id,
  gemeente AS gemeentecode,
  gemeente AS gemeentenaam,
  geometrie
FROM brk_gemeente
"""),
        migrate.ManageView(view_name='geo_lki_kadastralegemeente',
                           sql="""
SELECT
  id,
  id as code,
  geometrie
FROM brk_kadastralegemeente"""),

        migrate.ManageView(view_name='geo_lki_sectie',
                           sql="""
SELECT
    id,
    id AS volledige_code,
    sectie as code,
    geometrie
FROM brk_kadastralesectie
"""),
    ]
