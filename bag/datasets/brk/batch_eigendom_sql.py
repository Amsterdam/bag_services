sql_commands = ["DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_gemcluster_mat",
                "DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_sectiecluster_mat",
                "DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_filled_polygons_mat",
                "DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_poly_mat",
                "DROP MATERIALIZED VIEW IF EXISTS brk_eigendom_point_mat",
                "DROP MATERIALIZED VIEW IF EXISTS brk_eigendommen_mat",
                "DROP VIEW IF EXISTS brk_eigenaar_niet_natuurlijk",
                "DROP VIEW IF EXISTS brk_eigenaar_overige_gemeente",
                "DROP VIEW IF EXISTS brk_eigenaar_spoorwegen",
                "DROP VIEW IF EXISTS brk_eigenaar_vve",
                "DROP VIEW IF EXISTS brk_eigenaar_woningcorporatie",
                "DROP VIEW IF EXISTS brk_eigenaar_waterschap",
                "DROP VIEW IF EXISTS brk_eigenaar_provincie",
                "DROP VIEW IF EXISTS brk_eigenaar_staat",
                "DROP VIEW IF EXISTS brk_eigenaar_gemeente",
                "DROP VIEW IF EXISTS brk_eigenaar_natuurlijk",
                """CREATE VIEW brk_eigenaar_natuurlijk AS SELECT 0 as cat_id, 'Natuurlijke persoon'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id is null""",
                """CREATE VIEW brk_eigenaar_gemeente AS SELECT 1 as cat_id, 'Amsterdam'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and (upper(ks.statutaire_naam) like '%AMSTERDAM%' or upper(ks.statutaire_naam) like '%STADSDEEL%')""",
                """CREATE VIEW brk_eigenaar_staat AS SELECT 3 as cat_id, 'De staat'::varchar as category, ks.* from brk_kadastraalsubject ks
       where (ks.rechtsvorm_id='5' or ks.rechtsvorm_id='10') and upper(ks.statutaire_naam) like '%DE STAAT%'""",
                """CREATE VIEW brk_eigenaar_provincie AS SELECT 4 as cat_id, 'Provincie'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and upper(ks.statutaire_naam) like '%PROVINCIE%'""",
                """CREATE VIEW brk_eigenaar_waterschap AS SELECT 5 as cat_id, 'Waterschap'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and (upper(ks.statutaire_naam) like '%WATERSCHAP%' or upper(ks.statutaire_naam) like '%HEEMRAADSCHAP%')""",
                """CREATE VIEW brk_eigenaar_overige_gemeente AS SELECT 2 as cat_id, 'Overige gemeenten'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and upper(ks.statutaire_naam) like '%GEMEENTE%' and ks.id not in (
               select id from brk_eigenaar_gemeente
               UNION
               select id from brk_eigenaar_staat
               UNION
               select id from brk_eigenaar_provincie
               UNION
               select id from brk_eigenaar_waterschap
       )""",
                """CREATE VIEW brk_eigenaar_woningcorporatie AS SELECT 6 as cat_id, 'Woningcorporatie'::varchar as category, ks.* from brk_kadastraalsubject ks
       where id in ('NL.KAD.Persoon.252140640','NL.KAD.Persoon.503138989','NL.KAD.Persoon.499112361',
       'NL.KAD.Persoon.172211115','NL.KAD.Persoon.478316430','NL.KAD.Persoon.11734470','NL.KAD.Persoon.519506319',
       'NL.KAD.Persoon.462322843','NL.KAD.Persoon.422423013','NL.KAD.Persoon.122930769','NL.KAD.Persoon.122912658',
       'NL.KAD.Persoon.172035933','NL.KAD.Persoon.308371616','NL.KAD.Persoon.202352911','NL.KAD.Persoon.326155554',
       'NL.KAD.Persoon.11734470','NL.KAD.Persoon.172013595','NL.KAD.Persoon.172013435','NL.KAD.Persoon.172013404',
       'NL.KAD.Persoon.172214610','NL.KAD.Persoon.11731803','NL.KAD.Persoon.311883303','NL.KAD.Persoon.199400597',
       'NL.KAD.Persoon.252140640','NL.KAD.Persoon.402718637','NL.KAD.Persoon.198921986','NL.KAD.Persoon.260547779',
       'NL.KAD.Persoon.172206338','NL.KAD.Persoon.172211115','NL.KAD.Persoon.333687163','NL.KAD.Persoon.197114580',
       'NL.KAD.Persoon.122620316','NL.KAD.Persoon.172209052','NL.KAD.Persoon.172090014','NL.KAD.Persoon.459362889',
       'NL.KAD.Persoon.406261333','NL.KAD.Persoon.172013385','NL.KAD.Persoon.331501954','NL.KAD.Persoon.260334994',
       'NL.KAD.Persoon.184029003','NL.KAD.Persoon.197352789','NL.KAD.Persoon.172219833','NL.KAD.Persoon.172107996')""",
                """CREATE VIEW brk_eigenaar_vve AS SELECT 7 as cat_id, 'VVE'::varchar as category, ks.* from brk_kadastraalsubject ks
       where (ks.rechtsvorm_id='13' or ks.rechtsvorm_id='21')""",
                """CREATE VIEW brk_eigenaar_spoorwegen AS SELECT 8 as cat_id, 'Spoorwegen'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id not in ('13', '21', '27') and
             (upper(ks.statutaire_naam) like 'NS VAST%' or upper(ks.statutaire_naam) like '%SPOORWEGEN%' OR
              upper(ks.statutaire_naam) like '%RAILINFRA%' or upper(ks.statutaire_naam) like '%PRORAIL%')""",
                """CREATE VIEW brk_eigenaar_niet_natuurlijk AS SELECT 9 as cat_id, 'Overig niet natuurlijk'::varchar as category, ks.* from brk_kadastraalsubject ks
       where ks.id not in (
               select id from brk_eigenaar_gemeente
               UNION
               select id from brk_eigenaar_overige_gemeente
               UNION
               select id from brk_eigenaar_staat
               UNION
               select id from brk_eigenaar_provincie
               UNION
               select id from brk_eigenaar_waterschap
               UNION
               select id from brk_eigenaar_woningcorporatie
               UNION
               select id from brk_eigenaar_vve
               UNION
               select id from brk_eigenaar_spoorwegen
               UNION
               select id from brk_eigenaar_natuurlijk
       )""",
                "DROP TABLE IF EXISTS brk_eigenaren_categorie",
                "DROP TABLE IF EXISTS brk_eigenaren",
                "DROP TABLE IF EXISTS brk_bebouwde_g_percelen",
                "DROP TABLE IF EXISTS brk_bebouwde_a_percelen",
                "DROP TABLE IF EXISTS brk_eigendommen",
                """create table brk_eigenaren
               as
                       select * from brk_eigenaar_natuurlijk
                       UNION
                       select * from brk_eigenaar_gemeente
                       UNION
                       select * from brk_eigenaar_overige_gemeente
                       UNION
                       select * from brk_eigenaar_staat
                       UNION
                       select * from brk_eigenaar_provincie
                       UNION
                       select * from brk_eigenaar_waterschap
                       UNION
                       select * from brk_eigenaar_woningcorporatie
                       UNION
                       select * from brk_eigenaar_vve
                       UNION
                       select * from brk_eigenaar_spoorwegen
                       UNION
                       select * from brk_eigenaar_niet_natuurlijk""",
                """create table brk_eigenaren_categorie
               as
                       select cat_id, category from brk_eigenaren group by 1, 2 order by 1""",
                "DROP VIEW IF EXISTS brk_eigenaar_niet_natuurlijk",
                "DROP VIEW IF EXISTS brk_eigenaar_overige_gemeente",
                "DROP VIEW IF EXISTS brk_eigenaar_spoorwegen",
                "DROP VIEW IF EXISTS brk_eigenaar_vve",
                "DROP VIEW IF EXISTS brk_eigenaar_woningcorporatie",
                "DROP VIEW IF EXISTS brk_eigenaar_waterschap",
                "DROP VIEW IF EXISTS brk_eigenaar_provincie",
                "DROP VIEW IF EXISTS brk_eigenaar_staat",
                "DROP VIEW IF EXISTS brk_eigenaar_gemeente",
                "DROP VIEW IF EXISTS brk_eigenaar_natuurlijk",
                """create table brk_bebouwde_g_percelen as
               SELECT *
               FROM brk_zakelijkrecht
               WHERE substring(_kadastraal_object_aanduiding FROM 15 FOR 1) = 'G'
                     AND (kadastraal_object_id IN (SELECT kadastraal_object_id
                                                   FROM brk_kadastraalobjectverblijfsobjectrelatie
                                                   WHERE verblijfsobject_id IS NOT NULL)
                          OR kadastraal_object_id IN (SELECT id
                                                      FROM brk_kadastraalobject
                                                      WHERE
                                                              cultuurcode_onbebouwd_id IN ('92', '93') OR (
                                                                      cultuurcode_bebouwd_id IS NOT NULL
                                                                      AND cultuurcode_bebouwd_id NOT IN ('', '18', '18, 34', '18, 99', '34', '34, 99', '44', '46', '94', '99')
                                                              )))""",
                """create table brk_bebouwde_a_percelen as
               SELECT *
               FROM brk_zakelijkrecht
               WHERE substring(_kadastraal_object_aanduiding FROM 15 FOR 1) = 'A'
                     AND (kadastraal_object_id IN (SELECT kadastraal_object_id
                                                   FROM brk_kadastraalobjectverblijfsobjectrelatie
                                                   WHERE verblijfsobject_id IS NOT NULL)
                          OR kadastraal_object_id IN (SELECT id
                                                      FROM brk_kadastraalobject
                                                      WHERE
                                                              cultuurcode_onbebouwd_id IN ('92', '93') OR (
                                                                      cultuurcode_bebouwd_id IS NOT NULL
                                                                      AND cultuurcode_bebouwd_id NOT IN ('', '18', '18, 34', '18, 99', '34', '34, 99', '44', '46', '94', '99')
                                                              )))""",
                """create table brk_eigendommen
               AS
                       select zr.id, zr.kadastraal_subject_id, zr.kadastraal_object_id, zr.aard_zakelijk_recht_akr, eig.cat_id, false::boolean as grondeigenaar, false::boolean as aanschrijfbaar, false::boolean as appartementeigenaar
                     from brk_eigenaren eig, brk_zakelijkrecht  zr where zr.kadastraal_subject_id = eig.id""",
                "update brk_eigendommen set grondeigenaar = true where id in (select id from brk_zakelijkrecht where aard_zakelijk_recht_id = '2' and substring(_kadastraal_object_aanduiding from 15 for 1) = 'G')",
                "update brk_eigendommen set aanschrijfbaar = true where id in (select id from brk_bebouwde_g_percelen where aard_zakelijk_recht_id in ('3','4','7','12','13'))",
                """update brk_eigendommen set aanschrijfbaar = true where id in (select id from brk_bebouwde_g_percelen bbgp where aard_zakelijk_recht_id = '2' and kadastraal_object_id not in (
               select kadastraal_object_id from brk_bebouwde_g_percelen bbgp where bbgp.aard_zakelijk_recht_id in ('3','4','7','12','13')
       )) and aanschrijfbaar = false::boolean""",
                """update brk_eigendommen set aanschrijfbaar = true where id in (select id from brk_bebouwde_g_percelen bbgp where aard_zakelijk_recht_id = '2' and kadastraal_object_id in (
               select kadastraal_object_id FROM
                       (SELECT
                               kadastraal_object_id,
                               aard_zakelijk_recht_id
                       FROM brk_bebouwde_g_percelen
                       GROUP BY 1, 2) a
                       GROUP BY 1
                       HAVING count(a.aard_zakelijk_recht_id) = 1
               )) and aanschrijfbaar = false::boolean""",
                """update brk_eigendommen set appartementeigenaar = true where id in (select id from brk_bebouwde_a_percelen where aard_zakelijk_recht_id in ('3','4','7','12','13'))""",
                """update brk_eigendommen set appartementeigenaar = true where id in (select id from brk_bebouwde_a_percelen bbgp where aard_zakelijk_recht_id = '2' and kadastraal_object_id not in (
               select kadastraal_object_id from brk_bebouwde_a_percelen bbgp where bbgp.aard_zakelijk_recht_id in ('3','4','7','12','13')
       )) and appartementeigenaar = false::boolean""",
                """update brk_eigendommen set appartementeigenaar = true where id in (select id from brk_bebouwde_a_percelen bbgp where aard_zakelijk_recht_id = '2' and kadastraal_object_id in (
               select kadastraal_object_id FROM
                       (SELECT
                                kadastraal_object_id,
                                aard_zakelijk_recht_id
                        FROM brk_bebouwde_a_percelen
                        GROUP BY 1, 2) a
               GROUP BY 1
               HAVING count(a.aard_zakelijk_recht_id) = 1
       )) and appartementeigenaar = false::boolean""",
                #   Base materialized view for cartographic layers,
                #       categorized registry-objects - only outright ownership
                """CREATE MATERIALIZED VIEW brk_eigendommen_mat AS (SELECT
               row_number() over () AS id,
               eigendom.kadastraal_object_id,
               eigendom.cat_id,
               kot.poly_geom,
               kot.point_geom
       FROM
               (SELECT kadastraal_object_id, cat_id
                FROM brk_eigendommen
                WHERE aard_zakelijk_recht_akr = 'VE'
            GROUP BY 1, 2) eigendom, brk_kadastraalobject kot
       WHERE kot.id = eigendom.kadastraal_object_id)""",
                "CREATE INDEX eigendommen_poly ON brk_eigendommen_mat USING GIST (poly_geom)",
                "CREATE INDEX eigendommen_point ON brk_eigendommen_mat USING GIST (point_geom)",
                #   Based on previous materialized view:
                #       Materialized view for cartographic layers, grouped point-geometries together per polygon
                #       Used for showing counts of point-geom properties (appartements and the like) per poly-geom
                #       (usually land plots)
                """CREATE MATERIALIZED VIEW brk_eigendom_point_mat AS Select
       poly.kadastraal_object_id as id, point.cat_id, poly.poly_geom, st_centroid(st_union(point.point_geom)) as geometrie, count(point.point_geom) as aantal
       from brk_eigendommen_mat poly, brk_eigendommen_mat point where poly.poly_geom is not null and point.point_geom is not NULL
               and st_within(point.point_geom, poly.poly_geom) group by 1, 2, 3""",
                "CREATE INDEX eigendom_point ON brk_eigendom_point_mat USING GIST (geometrie)",
                #   Based on outright ownership categorized base materialized view:
                #       Materialized view for cartographic layers, grouped polygons (as unnested multipolygons)
                #       per category of the encompassing polygons by which the previous materialized view is grouped by
                """CREATE MATERIALIZED VIEW brk_eigendom_filled_polygons_mat AS Select
               row_number() over () AS id,
               cat_id,
               ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
       FROM (SELECT st_union(poly_geom) geom, cat_id from brk_eigendom_point_mat group by cat_id) as subquery""",
                "CREATE INDEX eigendom_point_niet_poly ON brk_eigendom_filled_polygons_mat USING GIST (geometrie)",
                #   Based on outright ownership categorized base materialized view:
                #       Materialized view for cartographic layers, grouped polygons (as unnested multipolygons) per category
                #       Used for showing lines around grouped counts of point-geom properties
                #           (appartements and the like) per poly-geom (land plots) which have a mixed ownership
                """CREATE MATERIALIZED VIEW brk_eigendom_poly_mat AS Select
               row_number() over () AS id,
               cat_id,
               ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
       FROM (SELECT st_union(poly_geom) geom, cat_id from brk_eigendommen_mat group by cat_id) as subquery""",
                "CREATE INDEX eigendom_poly ON brk_eigendom_poly_mat USING GIST (geometrie)",
                #   Based on outright ownership categorized base materialized view:
                #       Materialized view for cartographic layers, grouped polygons (as unnested multipolygons) per category
                #       Used for showing lines around grouped counts of point-geom properties
                #           (appartements and the like) per poly-geom (land plots) which have a same type of ownership
                """CREATE MATERIALIZED VIEW brk_eigendom_point_sectiecluster_mat AS SELECT
               pt.cat_id, ks.id, st_centroid(ks.geometrie) as geometrie, count(obj.*) as aantal
       FROM brk_eigendommen_mat pt, brk_kadastraalobject obj, brk_kadastralesectie ks
       where pt.kadastraal_object_id = obj.id and obj.sectie_id = ks.id and pt.point_geom is not null
       GROUP BY 1, 2""",
                #   Based on outright ownership categorized base materialized view:
                #       Materialized view for cartographic layers, grouped points per registry-municipality
                """CREATE MATERIALIZED VIEW brk_eigendom_point_gemcluster_mat AS SELECT
               pt.cat_id, kg.id, st_centroid(kg.geometrie) as geometrie, count(obj.*) as aantal
       FROM brk_eigendommen_mat pt, brk_kadastraalobject obj, brk_kadastralegemeente kg
       where pt.kadastraal_object_id = obj.id and obj.kadastrale_gemeente_id = kg.id and pt.point_geom is not null
       GROUP BY 1, 2""",
                ]
