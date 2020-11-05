# -*- coding: utf-8 -*-

from django.db import migrations

from geo_views import migrate

from django.conf import settings

from psycopg2.extensions import QuotedString

URL = settings.DATAPUNT_API_URL


class Migration(migrations.Migration):
    replaces = [('geo_views', '0001_bag_views'), ('geo_views', '0002_lki_views'), ('geo_views', '0003_wkpb_views'),  # noqa
                ('geo_views', '0004_lki_views'), ('geo_views', '0005_bag_views'), ('geo_views', '0006_bag_views'),   # noqa
                ('geo_views', '0007_update_views'), ('geo_views', '0008_wkpb_view'), ('geo_views', '0009_bag_opr_view'), # noqa
                ('geo_views', '0010_brk_wkpb_views')]

    dependencies = [
        ('bag', '0001_initial'),
        ('brk', '0001_initial'),
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
  'gebieden/bouwblok'::TEXT                           AS type,
  {} || 'gebieden/bouwblok/' || bb.id || '/' AS uri
FROM
  bag_bouwblok bb
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_buurt',
            sql="""
SELECT
  b.id                                            AS id,
  b.code                                          AS code,
  b.vollcode                                      AS vollcode,
  b.naam                                          AS naam,
  b.geometrie                                     AS geometrie,
  b.naam                                          AS display,
  'gebieden/buurt'::TEXT                          AS type,
  {} || 'gebieden/buurt/' || b.id || '/' AS uri
FROM bag_buurt b
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_buurt_simple',
            sql="""
SELECT
  b.id                                             AS id,
  b.code                                           AS code,
  b.vollcode                                       AS vollcode,
  b.naam                                           AS naam,
  ST_SimplifyPreserveTopology(b.geometrie, 0.1)    AS geometrie,
  b.naam                                           AS display,
  'gebieden/buurt'::TEXT                           AS type,
  {} || 'gebieden/buurt/' || b.id || '/' AS uri
FROM bag_buurt b
""".format(QuotedString(URL)),
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
  'gebieden/buurtcombinatie'::TEXT                           AS type,
  {} || 'gebieden/buurtcombinatie/' || bc.id || '/' AS uri
FROM bag_buurtcombinatie bc
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_buurtcombinatie_simple',
            sql="""
SELECT
  bc.id                                                      AS id,
  bc.vollcode                                                AS vollcode,
  bc.naam                                                    AS naam,
  ST_SimplifyPreserveTopology(bc.geometrie, 0.1)             AS geometrie,
  bc.naam                                                    AS display,
  'gebieden/buurtcombinatie'::TEXT                           AS type,
  {} || 'gebieden/buurtcombinatie/' || bc.id || '/' AS uri
FROM bag_buurtcombinatie bc
""".format(QuotedString(URL)),
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
  'gebieden/gebiedsgerichtwerken'::TEXT                          AS type,
  {} || 'gebieden/gebiedsgerichtwerken/' || g.id || '/' AS uri
FROM bag_gebiedsgerichtwerken g
""".format(QuotedString(URL)),
        ),
        migrate.ManageView(
            view_name='geo_bag_grootstedelijkgebied',
            sql="""
SELECT
  gg.id                                                           AS id,
  gg.naam                                                         AS naam,
  gg.geometrie                                                    AS geometrie,
  gg.naam                                                         AS display,
  'gebieden/grootstedelijkgebied'::TEXT                           AS type,
  {} || 'gebieden/grootstedelijkgebied/' || gg.id || '/' AS uri
FROM bag_grootstedelijkgebied gg
""".format(QuotedString(URL)),
        ),
        migrate.ManageView(
            view_name='geo_bag_ligplaats',
            sql="""
SELECT
  l.landelijk_id                    AS id,
  l.geometrie                       AS geometrie,
  'bag/ligplaats'::TEXT             AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE('-' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                 AS display,
  {} || 'bag/v1.1/ligplaats/' || l.landelijk_id || '/' AS uri

FROM bag_ligplaats l
  LEFT JOIN bag_nummeraanduiding n ON n.ligplaats_id = l.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
WHERE
  n.type_adres = 'Hoofdadres'
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_openbareruimte',
            sql="""
SELECT
  opr.landelijk_id                                      AS id,
  opr.naam                                              AS display,
  opr.omschrijving                                      AS omschrijving,
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
  {} || 'bag/v1.1/openbareruimte/' || opr.landelijk_id || '/' AS uri
FROM
  bag_openbareruimte opr
""".format(QuotedString(URL))
        ),

        migrate.ManageView(
            view_name='geo_bag_pand',
            sql="""
SELECT
  p.landelijk_id                            AS id,
  p.geometrie                               AS geometrie,
  p.landelijk_id                            AS display,
  'bag/pand'::TEXT                          AS type,
  {} || 'bag/v1.1/pand/' || p.landelijk_id || '/'       AS uri
FROM
  bag_pand p
""".format(QuotedString(URL)),
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
  'gebieden/stadsdeel'::TEXT                          AS type,
  {} || 'gebieden/stadsdeel/' || s.id || '/' AS uri
FROM bag_stadsdeel s
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_standplaats',
            sql="""
SELECT
  s.landelijk_id                                AS id,
  s.geometrie                                   AS geometrie,
  'bag/standplaats'::TEXT                       AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE(' ' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                             AS display,
  {} || 'bag/v1.1/standplaats/' || s.landelijk_id || '/' AS uri

FROM bag_standplaats s
  LEFT JOIN bag_nummeraanduiding n ON n.standplaats_id = s.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
WHERE
    n.type_adres = 'Hoofdadres'
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_unesco',
            sql="""
SELECT
  u.id                                             AS id,
  u.naam                                           AS naam,
  u.geometrie                                      AS geometrie,
  u.naam                                           AS display,
  'gebieden/unesco'::TEXT                          AS type,
  {} || 'gebieden/unesco/' || u.id || '/' AS uri
FROM bag_unesco u
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_bag_verblijfsobject',
            sql="""
SELECT
  v.landelijk_id                          AS id,
  v.geometrie                             AS geometrie,
  'bag/verblijfsobject'::TEXT             AS type,
  (o.naam || ' '
   || n.huisnummer || COALESCE(n.huisletter, '')
   || COALESCE('-' || NULLIF(n.huisnummer_toevoeging, ''), '')
  )                                       AS display,
  {} || 'bag/v1.1/verblijfsobject/' || v.landelijk_id || '/' AS uri

FROM bag_verblijfsobject v
  LEFT JOIN bag_nummeraanduiding n ON n.verblijfsobject_id = v.id
  LEFT JOIN bag_openbareruimte o ON n.openbare_ruimte_id = o.id
WHERE
    n.type_adres = 'Hoofdadres'
""".format(QuotedString(URL)),
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
            sql="""
SELECT
  ko.id                                                     AS id,
  ko.aanduiding                                             AS volledige_code,
  ko.perceelnummer                                          AS perceelnummer,
  coalesce(ko.point_geom, ko.poly_geom)                     AS geometrie,
  ko.aanduiding                                             AS display,
  'kadaster/kadastraal_object'::TEXT                        AS type,
  {} || 'brk/object/' || ko.id || '/' AS uri
FROM brk_kadastraalobject ko
""".format(QuotedString(URL)),
        ),

        migrate.ManageView(
            view_name='geo_lki_kadastraalobject',
            sql="""
SELECT
  ko.id                                                     AS id,
  ko.aanduiding                                             AS volledige_code,
  ko.perceelnummer                                          AS perceelnummer,
  coalesce(ko.point_geom, ko.poly_geom)                     AS geometrie,
  g.id || ' ' ||
  s.sectie || ' ' ||
  RIGHT('00000' || CAST(ko.perceelnummer AS VARCHAR), 5) || ' ' ||
  ko.indexletter || ' ' ||
  RIGHT('0000' || CAST(ko.indexnummer AS VARCHAR), 4)
                                                            AS display,
  'kadaster/kadastraal_object'::TEXT                        AS type,
  {} || 'brk/object/' || ko.id || '/' AS uri
FROM brk_kadastraalobject ko
LEFT JOIN brk_kadastralegemeente g ON g.id=ko.kadastrale_gemeente_id
LEFT JOIN brk_kadastralesectie s ON s.id=ko.sectie_id
""".format(QuotedString(URL))
        ),

        migrate.ManageView(
            view_name='geo_lki_kadastralegemeente',
            sql="""
SELECT
  id,
  id as code,
  geometrie,
  geometrie_lines
FROM brk_kadastralegemeente""",
        ),
        migrate.ManageView(
            view_name='geo_lki_sectie',
            sql="""
SELECT
    id,
    CONCAT(kadastrale_gemeente_id, ' ', sectie) AS volledige_code,
    sectie as code,
    geometrie,
    geometrie_lines
FROM brk_kadastralesectie
""",
        ),
    ]
