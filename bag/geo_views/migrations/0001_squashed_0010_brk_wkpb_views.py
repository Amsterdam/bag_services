# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate

from django.conf import settings

URL = settings.DATAPUNT_API_URL


class Migration(migrations.Migration):
    replaces = [('geo_views', '0001_bag_views'), ('geo_views', '0002_lki_views'), ('geo_views', '0003_wkpb_views'),  # noqa
                ('geo_views', '0004_lki_views'), ('geo_views', '0005_bag_views'), ('geo_views', '0006_bag_views'),   # noqa
                ('geo_views', '0007_update_views'), ('geo_views', '0008_wkpb_view'), ('geo_views', '0009_bag_opr_view'), # noqa
                ('geo_views', '0010_brk_wkpb_views')]

    dependencies = [
        ('wkpb', '0001_squashed_0010_auto_20151221_1123'),
        ('bag', '0007_auto_20161110_1548'),
        ('brk', '0034_kadastraalobject_geom_point'),
    ]

    operations = [
        migrate.ManageView(
            view_name='geo_bag_bouwblok',
            sql=f"""
SELECT
  bb.id                                               AS id,
  bb.code                                             AS code,
  bb.geometrie                                        AS geometrie,
  bb.code                                             AS display,
  'gebieden/bouwblok'::TEXT                           AS type,
  '{URL}' || 'gebieden/bouwblok/' || bb.id || '/' AS uri
FROM
  bag_bouwblok bb
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_buurt',
            sql=f"""
SELECT
  b.id                                            AS id,
  b.code                                          AS code,
  b.naam                                          AS naam,
  b.geometrie                                     AS geometrie,
  b.naam                                          AS display,
  'gebieden/buurt'::TEXT                          AS type,
  '{URL}' || 'gebieden/buurt/' || b.id || '/' AS uri
FROM bag_buurt b
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_buurtcombinatie',
            sql=f"""
SELECT
  bc.id                                                      AS id,
  bc.vollcode                                                AS vollcode,
  bc.naam                                                    AS naam,
  bc.geometrie                                               AS geometrie,
  bc.naam                                                    AS display,
  'gebieden/buurtcombinatie'::TEXT                           AS type,
  '{URL}' || 'gebieden/buurtcombinatie/' || bc.id || '/' AS uri
FROM bag_buurtcombinatie bc
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_gebiedsgerichtwerken',
            sql=f"""
SELECT
  g.id                                                           AS id,
  g.code                                                         AS code,
  g.naam                                                         AS naam,
  g.geometrie                                                    AS geometrie,
  g.naam                                                         AS display,
  'gebieden/gebiedsgerichtwerken'::TEXT                          AS type,
  '{URL}' || 'gebieden/gebiedsgerichtwerken/' || g.id || '/' AS uri
FROM bag_gebiedsgerichtwerken g
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_grootstedelijkgebied',
            sql=f"""
SELECT
  gg.id                                                           AS id,
  gg.naam                                                         AS naam,
  gg.geometrie                                                    AS geometrie,
  gg.naam                                                         AS display,
  'gebieden/grootstedelijkgebied'::TEXT                           AS type,
  '{URL}' || 'gebieden/grootstedelijkgebied/' || gg.id || '/' AS uri
FROM bag_grootstedelijkgebied gg
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_ligplaats',
            sql=f"""
SELECT
  l.landelijk_id                    AS id,
  l.geometrie                       AS geometrie,
  'bag/ligplaats'::TEXT             AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE('-' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                 AS display,
 '{URL}' || 'bag/ligplaats/' || l.id || '/' AS uri

FROM bag_ligplaats l
  LEFT JOIN bag_nummeraanduiding n ON n.ligplaats_id = l.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
WHERE
  n.hoofdadres
""",
        ),

        migrate.ManageView(
            view_name='geo_bag_openbareruimte',
            sql=f"""
SELECT
  opr.landelijk_id                                      AS id,
  opr.naam                                              AS display,
  CASE opr.type
    WHEN '01' THEN 'Weg'
        WHEN '02' THEN 'Water'
        WHEN '03' THEN 'Spoorbaan'
        WHEN '04' THEN 'Terrein'
        WHEN '05' THEN 'Kunstwerk'
        WHEN '06' THEN 'Landschappelijk gebied'
        WHEN '07' THEN 'Administratief gebied'
        ELSE '??'
  END                                                   AS opr_type,
  opr.geometrie                                         AS geometrie,
  'bag/openbareruimte'::TEXT                            AS type,
  '{URL}' || 'bag/openbareruimte/' || opr.id || '/' AS uri
FROM
  bag_openbareruimte opr
                """),

        migrate.ManageView(
            view_name='geo_bag_pand',
            sql=f"""
SELECT
  p.landelijk_id                            AS id,
  p.geometrie                               AS geometrie,
  p.landelijk_id                            AS display,
  'bag/pand'::TEXT                          AS type,
  '{URL}' || 'bag/pand/' || p.id || '/'       AS uri
FROM
  bag_pand p
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_stadsdeel',
            sql=f"""
SELECT
  s.id                                                AS id,
  s.code                                              AS code,
  s.naam                                              AS naam,
  s.geometrie                                         AS geometrie,
  s.naam                                              AS display,
  'gebieden/stadsdeel'::TEXT                          AS type,
  '{URL}' || 'gebieden/stadsdeel/' || s.id || '/' AS uri
FROM bag_stadsdeel s
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_standplaats',
            sql=f"""
SELECT
  s.landelijk_id                                AS id,
  s.geometrie                                   AS geometrie,
  'bag/standplaats'::TEXT                       AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE(' ' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                             AS display,
 '{URL}' || 'bag/standplaats/' || s.id || '/' AS uri

FROM bag_standplaats s
  LEFT JOIN bag_nummeraanduiding n ON n.standplaats_id = s.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
WHERE
  n.hoofdadres
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_unesco',
            sql=f"""
SELECT
  u.id                                             AS id,
  u.naam                                           AS naam,
  u.geometrie                                      AS geometrie,
  u.naam                                           AS display,
  'gebieden/unesco'::TEXT                          AS type,
  '{URL}' || 'gebieden/unesco/' || u.id || '/' AS uri
FROM bag_unesco u
""",
        ),
        migrate.ManageView(
            view_name='geo_bag_verblijfsobject',
            sql=f"""
SELECT
  v.landelijk_id                          AS id,
  v.geometrie                             AS geometrie,
  'bag/verblijfsobject'::TEXT             AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE('-' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                       AS display,
  '{URL}' || 'bag/verblijfsobject/' || v.id || '/' AS uri

FROM bag_verblijfsobject v
  LEFT JOIN bag_nummeraanduiding n ON n.verblijfsobject_id = v.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
WHERE
  n.hoofdadres
""",
        ),
        migrate.ManageView(
            view_name='geo_lki_gemeente',
            sql="""
SELECT
  gemeente AS id,
  gemeente AS gemeentecode,
  gemeente AS gemeentenaam,
  geometrie
FROM brk_gemeente
""",
        ),

        migrate.ManageView(
            view_name='geo_lki_kadastraalobject',
            sql=f"""
SELECT
  ko.id                                                     AS id,
  ko.aanduiding                                             AS volledige_code,
  ko.perceelnummer                                          AS perceelnummer,
  coalesce(ko.point_geom, ko.poly_geom)                     AS geometrie,
  ko.aanduiding                                             AS display,
  'kadaster/kadastraal_object'::TEXT                        AS type,
  '{URL}' || 'brk/object/' || ko.id || '/' AS uri
FROM brk_kadastraalobject ko
""",
        ),


        migrate.ManageView(
            view_name='geo_lki_kadastralegemeente',
            sql="""
SELECT
  id,
  id as code,
  geometrie
FROM brk_kadastralegemeente""",
        ),
        migrate.ManageView(
            view_name='geo_lki_sectie',
            sql="""
SELECT
    id,
    CONCAT(kadastrale_gemeente_id, ' ', sectie) AS volledige_code,
    sectie as code,
    geometrie
FROM brk_kadastralesectie
""",
        ),
        migrate.ManageView(
            view_name='geo_wkpb',
            sql=f"""
SELECT
  bk.id                                            AS id,
  bp.beperkingtype_id                              AS beperkingtype_id,
  coalesce(ko.point_geom, ko.poly_geom)            AS geometrie,
  bc.omschrijving                                  AS display,
  'wkpb/beperking'::TEXT                           AS type,
  '{URL}' || 'wkpb/beperking/' || bp.id || '/' AS uri
FROM
  wkpb_beperkingkadastraalobject bk
  LEFT JOIN wkpb_beperking bp ON bp.id = bk.beperking_id
  LEFT JOIN brk_kadastraalobject ko ON ko.id = bk.kadastraal_object_id
  LEFT JOIN wkpb_beperkingcode bc ON bc.code = bp.beperkingtype_id
WHERE
  bp.beperkingtype_id <> 'HS'
          """,
        ),
    ]
