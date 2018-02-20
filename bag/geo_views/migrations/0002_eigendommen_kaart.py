# -*- coding: utf-8 -*-

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('geo_views', '0001_squashed_0010_brk_wkpb_views'),
    ]

    operations = [
        migrations.RunSQL(
            [("""CREATE MATERIALIZED VIEW brk_eigendommen_mat AS (WITH
						brk_eigenaar_natuurlijk AS
				(SELECT
						 0                     AS cat_id,
						 'Natuurlijke persoon' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.rechtsvorm_id IS NULL),
						brk_eigenaar_gemeente AS
				(SELECT
						 1           AS cat_id,
						 'Amsterdam' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.rechtsvorm_id = '10' AND (upper(ks.statutaire_naam) LIKE '%AMSTERDAM%' OR
				                                    upper(ks.statutaire_naam) LIKE '%STADSDEEL%')),
						brk_eigenaar_overige_gemeente AS
				(SELECT
						 2                   AS cat_id,
						 'Overige gemeenten' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.rechtsvorm_id = '10' AND ks.id NOT IN (SELECT id FROM brk_eigenaar_gemeente)),
						brk_eigenaar_staat AS
				(SELECT
						 3          AS cat_id,
						 'De staat' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE (ks.rechtsvorm_id = '5' OR ks.rechtsvorm_id = '10') AND
				       upper(ks.statutaire_naam) LIKE '%DE STAAT%'),
						brk_eigenaar_provincie AS
				(SELECT
						 4           AS cat_id,
						 'Provincie' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.rechtsvorm_id = '10' AND upper(ks.statutaire_naam) LIKE '%PROVINCIE%'),
						brk_eigenaar_waterschap AS
				(SELECT
						 5            AS cat_id,
						 'Waterschap' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.rechtsvorm_id = '10' AND
				       (upper(ks.statutaire_naam) LIKE '%WATERSCHAP%' OR
				        upper(ks.statutaire_naam) LIKE '%HEEMRAADSCHAP%')),

						brk_eigenaar_woningcorporatie AS
				(SELECT
						 6                  AS cat_id,
						 'Woningcorporatie' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE id IN
				       ('NL.KAD.Persoon.252140640', 'NL.KAD.Persoon.503138989', 'NL.KAD.Persoon.499112361',
				        'NL.KAD.Persoon.172211115', 'NL.KAD.Persoon.478316430', 'NL.KAD.Persoon.11734470', 'NL.KAD.Persoon.519506319',
				        'NL.KAD.Persoon.462322843', 'NL.KAD.Persoon.422423013', 'NL.KAD.Persoon.122930769', 'NL.KAD.Persoon.122912658',
						'NL.KAD.Persoon.172035933', 'NL.KAD.Persoon.308371616', 'NL.KAD.Persoon.202352911', 'NL.KAD.Persoon.326155554',
						'NL.KAD.Persoon.11734470', 'NL.KAD.Persoon.172013595', 'NL.KAD.Persoon.172013435', 'NL.KAD.Persoon.172013404',
						'NL.KAD.Persoon.172214610', 'NL.KAD.Persoon.11731803', 'NL.KAD.Persoon.311883303', 'NL.KAD.Persoon.199400597',
						'NL.KAD.Persoon.252140640', 'NL.KAD.Persoon.402718637', 'NL.KAD.Persoon.198921986', 'NL.KAD.Persoon.260547779',
						'NL.KAD.Persoon.172206338', 'NL.KAD.Persoon.172211115', 'NL.KAD.Persoon.333687163', 'NL.KAD.Persoon.197114580',
						'NL.KAD.Persoon.122620316', 'NL.KAD.Persoon.172209052', 'NL.KAD.Persoon.172090014', 'NL.KAD.Persoon.459362889',
						'NL.KAD.Persoon.406261333', 'NL.KAD.Persoon.172013385', 'NL.KAD.Persoon.331501954', 'NL.KAD.Persoon.260334994',
						'NL.KAD.Persoon.184029003', 'NL.KAD.Persoon.197352789', 'NL.KAD.Persoon.172219833', 'NL.KAD.Persoon.172107996')),
						brk_eigenaar_vve AS
				(SELECT
						 7     AS cat_id,
						 'VVE' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE (ks.rechtsvorm_id = '13' OR ks.rechtsvorm_id = '21')),
						brk_eigenaar_spoorwegen AS
				(SELECT
						 8            AS cat_id,
						 'Spoorwegen' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.rechtsvorm_id NOT IN ('13', '21', '27') AND
				       (upper(ks.statutaire_naam) LIKE 'NS VAST%' OR
				        upper(ks.statutaire_naam) LIKE '%SPOORWEGEN%' OR
				        upper(ks.statutaire_naam) LIKE '%RAILINFRA%' OR
				        upper(ks.statutaire_naam) LIKE '%PRORAIL%')),
						brk_eigenaar_niet_natuurlijk AS
				(SELECT
						 9                        AS cat_id,
						 'Overig niet natuurlijk' AS category,
						 ks.*
				 FROM brk_kadastraalsubject ks
				 WHERE ks.id NOT IN (
						 SELECT id FROM brk_eigenaar_gemeente
						 UNION
						 SELECT id FROM brk_eigenaar_overige_gemeente
						 UNION
						 SELECT id FROM brk_eigenaar_staat
						 UNION
						 SELECT id FROM brk_eigenaar_provincie
						 UNION
						 SELECT id FROM brk_eigenaar_waterschap
						 UNION
						 SELECT id FROM brk_eigenaar_woningcorporatie
						 UNION
						 SELECT id FROM brk_eigenaar_vve
						 UNION
						 SELECT id FROM brk_eigenaar_spoorwegen
						 UNION
						 SELECT id FROM brk_eigenaar_natuurlijk
				 ))
		SELECT
                row_number() over () AS id,
   				eigenaar.cat_id,
				recht.kadastraal_object_id,
				eigendom.poly_geom,
				eigendom.point_geom
		FROM (SELECT eigenaren.*
		      FROM (
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_gemeente
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_overige_gemeente
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_staat
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_provincie
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_waterschap
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_woningcorporatie
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_vve
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_spoorwegen
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_niet_natuurlijk
				           UNION
				           SELECT
						           id,
						           cat_id
				           FROM brk_eigenaar_natuurlijk) AS eigenaren)
				AS eigenaar,
				brk_kadastraalobject AS eigendom,
				(
						SELECT
								kadastraal_subject_id,
								kadastraal_object_id
						FROM brk_zakelijkrecht
						WHERE aard_zakelijk_recht_akr = 'VE'
				) AS recht
		WHERE eigenaar.id = recht.kadastraal_subject_id AND
		      recht.kadastraal_object_id = eigendom.id);""", None)],
            [("DROP MATERIALIZED VIEW IF EXISTS brk_eigendommen_mat;", None)],
        ),
        migrations.RunSQL([("CREATE INDEX eigendommen_poly ON brk_eigendommen_mat USING GIST (poly_geom);", None)],
                          [("DROP INDEX IF EXISTS eigendommen_poly;", None)]),
        migrations.RunSQL([("CREATE INDEX eigendommen_point ON brk_eigendommen_mat USING GIST (point_geom);", None)],
                          [("DROP INDEX IF EXISTS eigendommen_point;", None)]),
        migrations.RunSQL([("""CREATE MATERIALIZED VIEW brk_eigendom_point_mat AS Select
poly.kadastraal_object_id as id, point.cat_id, poly.poly_geom, st_centroid(st_union(point.point_geom)) as geometrie, count(point.point_geom) as aantal
from brk_eigendommen_mat poly, brk_eigendommen_mat point where poly.poly_geom is not null and point.point_geom is not NULL
		and st_within(point.point_geom, poly.poly_geom) group by 1, 2, 3;""", None)],
                          [("DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_mat;", None)]),
        migrations.RunSQL([("CREATE INDEX eigendom_point ON brk_eigendom_point_mat USING GIST (geometrie);", None)],
                          [("DROP INDEX IF EXISTS eigendom_point;", None)]),
        migrations.RunSQL([("""CREATE MATERIALIZED VIEW brk_eigendom_poly_mat AS Select
   row_number() over () AS id,
   cat_id,
   gc as geometrie
from
   (SELECT (ST_Dump(geom)).geom AS gc, cat_id from
       (SELECT st_union(poly_geom) geom, cat_id from brk_eigendommen_mat group by cat_id) as inner_sub)
       as subquery;""", None)],
                          [("DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_poly_mat;", None)]),
        migrations.RunSQL([("CREATE INDEX eigendom_poly ON brk_eigendom_poly_mat USING GIST (geometrie);", None)],
                          [("DROP INDEX IF EXISTS eigendom_poly;", None)]),
        migrations.RunSQL([("""CREATE MATERIALIZED VIEW brk_eigendom_point_sectiecluster_mat AS SELECT
pt.cat_id, ks.id, st_centroid(ks.geometrie) as geometrie, sum(pt.aantal) as aantal
FROM brk_eigendom_point_mat pt, brk_kadastraalobject obj, brk_kadastralesectie ks
		where pt.id = obj.id and obj.sectie_id = ks.id
GROUP BY 1, 2;""", None)],
                          [("DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_sectiecluster_mat;", None)]),
        migrations.RunSQL([("""CREATE MATERIALIZED VIEW brk_eigendom_point_gemcluster_mat AS SELECT
     pt.cat_id, kg.id, st_centroid(kg.geometrie) as geometrie, sum(pt.aantal) as aantal
 FROM brk_eigendom_point_mat pt, brk_kadastraalobject obj, brk_kadastralegemeente kg
 where pt.id = obj.id and obj.kadastrale_gemeente_id = kg.id
 GROUP BY 1, 2;""", None)],
                          [("DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_gemcluster_mat;", None)]),
        migrations.RunSQL([("""CREATE MATERIALIZED VIEW brk_eigendom_point_niet_poly_mat AS Select
     row_number() over () AS id,
     cat_id,
     gc as geometrie
FROM (SELECT (ST_Dump(geom)).geom AS gc, cat_id from (SELECT st_union(poly_geom) geom, cat_id from brk_eigendom_point_mat group by cat_id) as inner_sub)
		as subquery;""", None)],
                          [("DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_niet_poly_mat;", None)]),
        migrations.RunSQL([("CREATE INDEX eigendom_point_niet_poly_idx ON brk_eigendom_point_niet_poly_mat USING GIST (geometrie);", None)],
                          [("DROP INDEX IF EXISTS eigendom_point_niet_poly_idx;", None)]),
    ]
