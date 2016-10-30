# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from geo_views import migrate


class Migration(migrations.Migration):
    replaces = [('geo_views', '0001_bag_views'), ('geo_views', '0002_lki_views'), ('geo_views', '0003_wkpb_views'),
                ('geo_views', '0004_lki_views'), ('geo_views', '0005_bag_views'), ('geo_views', '0006_bag_views'),
                ('geo_views', '0007_update_views'), ('geo_views', '0008_wkpb_view'), ('geo_views', '0009_bag_opr_view'),
                ('geo_views', '0010_brk_wkpb_views')]

    dependencies = [
        ('atlas_api', '0002_site_name'),
        ('wkpb', '0001_squashed_0010_auto_20151221_1123'),
        ('bag', '0001_squashed_0042_auto_20151210_0952'),
        ('sites', '0001_initial'),
        ('brk', '0021_auto_20151221_1123'),
    ]

    operations = [
        migrate.ManageView(
                view_name='geo_bag_bouwblok',
                sql="""
SELECT
  bb.id                                               AS id,
  bb.code                                             AS code,
  bb.geometrie                                        AS geometrie,
  bb.code                                             AS display,
  'gebieden/bouwblok'                                 AS type,
  site.domain || 'gebieden/bouwblok/' || bb.id || '/' AS uri
FROM
  bag_bouwblok bb
  ,
  django_site site
WHERE
  site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_buurt',
                sql="""
SELECT
  b.id                                            AS id,
  b.code                                          AS code,
  b.naam                                          AS naam,
  b.geometrie                                     AS geometrie,
  b.naam                                          AS display,
  'gebieden/buurt'                                AS type,
  site.domain || 'gebieden/buurt/' || b.id || '/' AS uri
FROM bag_buurt b, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_buurtcombinatie',
                sql="""
SELECT
  bc.id                                                      AS id,
  bc.vollcode                                                AS vollcode,
  bc.naam                                                    AS naam,
  bc.geometrie                                               AS geometrie,
  bc.naam                                                    AS display,
  'gebieden/buurtcombinatie'                                 AS type,
  site.domain || 'gebieden/buurtcombinatie/' || bc.id || '/' AS uri
FROM bag_buurtcombinatie bc, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_gebiedsgerichtwerken',
                sql="""
SELECT
  g.id                                                           AS id,
  g.code                                                         AS code,
  g.naam                                                         AS naam,
  g.geometrie                                                    AS geometrie,
  g.naam                                                         AS display,
  'gebieden/gebiedsgerichtwerken'                                AS type,
  site.domain || 'gebieden/gebiedsgerichtwerken/' || g.id || '/' AS uri
FROM bag_gebiedsgerichtwerken g, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_grootstedelijkgebied',
                sql="""
SELECT
  gg.id                                                           AS id,
  gg.naam                                                         AS naam,
  gg.geometrie                                                    AS geometrie,
  gg.naam                                                         AS display,
  'gebieden/grootstedelijkgebied'                                 AS type,
  site.domain || 'gebieden/grootstedelijkgebied/' || gg.id || '/' AS uri
FROM bag_grootstedelijkgebied gg, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_ligplaats',
                sql="""
SELECT
  l.id                              AS id,
  l.geometrie                       AS geometrie,
  'bag/ligplaats'                   AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE('-' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                 AS display,
  site.domain || 'bag/ligplaats/' || l.id || '/' AS uri

FROM bag_ligplaats l
  LEFT JOIN bag_nummeraanduiding n ON n.ligplaats_id = l.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
  ,
  django_site site
WHERE
  n.hoofdadres
  AND site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_openbareruimte',
                sql="""
SELECT
  opr.id                                                AS id,
  opr.naam                                              AS display,
  opr.type                                              AS opr_type,
  opr.geometrie                                         AS geometrie,
  'bag/openbareruimte'                                  AS type,
  site.domain || 'bag/openbareruimte/' || opr.id || '/' AS uri
FROM
  bag_openbareruimte opr
  ,
  django_site site
WHERE
  site.name = 'API Domain'
            """,
        ),
        migrate.ManageView(
                view_name='geo_bag_pand',
                sql="""
SELECT
  p.id                                      AS id,
  p.geometrie                               AS geometrie,
  p.landelijk_id                            AS display,
  'bag/pand'                                AS type,
  site.domain || 'bag/pand/' || p.id || '/' AS uri
FROM
  bag_pand p
  ,
  django_site site
WHERE
  site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_stadsdeel',
                sql="""
SELECT
  s.id                                                AS id,
  s.code                                              AS code,
  s.naam                                              AS naam,
  s.geometrie                                         AS geometrie,
  s.naam                                              AS display,
  'gebieden/stadsdeel'                                AS type,
  site.domain || 'gebieden/stadsdeel/' || s.id || '/' AS uri
FROM bag_stadsdeel s, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_standplaats',
                sql="""
SELECT
  s.id                                          AS id,
  s.geometrie                                   AS geometrie,
  'bag/standplaats'                             AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE(' ' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                             AS display,
  site.domain || 'bag/standplaats/' || s.id || '/' AS uri

FROM bag_standplaats s
  LEFT JOIN bag_nummeraanduiding n ON n.standplaats_id = s.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
  ,
  django_site site
WHERE
  n.hoofdadres
  AND site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_unesco',
                sql="""
SELECT
  u.id                                             AS id,
  u.naam                                           AS naam,
  u.geometrie                                      AS geometrie,
  u.naam                                           AS display,
  'gebieden/unesco'                                AS type,
  site.domain || 'gebieden/unesco/' || u.id || '/' AS uri
FROM bag_unesco u, django_site site
WHERE site.name = 'API Domain'
""",
        ),
        migrate.ManageView(
                view_name='geo_bag_verblijfsobject',
                sql="""
SELECT
  v.id                                    AS id,
  v.geometrie                             AS geometrie,
  'bag/verblijfsobject'                   AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE('-' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                       AS display,
  site.domain || 'bag/verblijfsobject/' || v.id || '/' AS uri

FROM bag_verblijfsobject v
  LEFT JOIN bag_nummeraanduiding n ON n.verblijfsobject_id = v.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
  ,
  django_site site
WHERE
  n.hoofdadres
  AND site.name = 'API Domain'
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
    id AS volledige_code,
    sectie as code,
    geometrie
FROM brk_kadastralesectie
""",
        ),
        migrate.ManageView(
                view_name='geo_wkpb',
                sql="""
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
          """,
        ),
    ]
