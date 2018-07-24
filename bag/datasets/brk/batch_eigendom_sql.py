sql_commands = ["DROP VIEW IF EXISTS brk_eigenaar_niet_natuurlijk",
                "DROP VIEW IF EXISTS brk_eigenaar_overige_gemeente",
                "DROP VIEW IF EXISTS brk_eigenaar_spoorwegen",
                "DROP VIEW IF EXISTS brk_eigenaar_vve",
                "DROP VIEW IF EXISTS brk_eigenaar_woningcorporatie",
                "DROP VIEW IF EXISTS brk_eigenaar_waterschap",
                "DROP VIEW IF EXISTS brk_eigenaar_provincie",
                "DROP VIEW IF EXISTS brk_eigenaar_staat",
                "DROP VIEW IF EXISTS brk_eigenaar_gemeente",
                "DROP VIEW IF EXISTS brk_eigenaar_natuurlijk",
                """CREATE VIEW brk_eigenaar_natuurlijk AS SELECT 0 as cat_id, 'Natuurlijke persoon'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id is null""",
                """CREATE VIEW brk_eigenaar_gemeente AS SELECT 1 as cat_id, 'Amsterdam'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and (upper(ks.statutaire_naam) like '%AMSTERDAM%' or upper(ks.statutaire_naam) like '%STADSDEEL%')""",
                """CREATE VIEW brk_eigenaar_staat AS SELECT 3 as cat_id, 'De staat'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where (ks.rechtsvorm_id='5' or ks.rechtsvorm_id='10') and upper(ks.statutaire_naam) like '%DE STAAT%'""",
                """CREATE VIEW brk_eigenaar_provincie AS SELECT 4 as cat_id, 'Provincie'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and upper(ks.statutaire_naam) like '%PROVINCIE%'""",
                """CREATE VIEW brk_eigenaar_waterschap AS SELECT 5 as cat_id, 'Waterschap'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and (upper(ks.statutaire_naam) like '%WATERSCHAP%' or upper(ks.statutaire_naam) like '%HEEMRAADSCHAP%')""",
                """CREATE VIEW brk_eigenaar_overige_gemeente AS SELECT 2 as cat_id, 'Overige gemeenten'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id='10' and upper(ks.statutaire_naam) like '%GEMEENTE%' and ks.id not in (
               select id from brk_eigenaar_gemeente
               UNION
               select id from brk_eigenaar_staat
               UNION
               select id from brk_eigenaar_provincie
               UNION
               select id from brk_eigenaar_waterschap
       )""",
                """CREATE VIEW brk_eigenaar_woningcorporatie AS SELECT 6 as cat_id, 'Woningcorporatie'::varchar as categorie, ks.* from brk_kadastraalsubject ks
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
                """CREATE VIEW brk_eigenaar_vve AS SELECT 7 as cat_id, 'VVE'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where (ks.rechtsvorm_id='13' or ks.rechtsvorm_id='21')""",
                """CREATE VIEW brk_eigenaar_spoorwegen AS SELECT 8 as cat_id, 'Spoorwegen'::varchar as categorie, ks.* from brk_kadastraalsubject ks
       where ks.rechtsvorm_id not in ('13', '21', '27') and
             (upper(ks.statutaire_naam) like 'NS VAST%' or upper(ks.statutaire_naam) like '%SPOORWEGEN%' OR
              upper(ks.statutaire_naam) like '%RAILINFRA%' or upper(ks.statutaire_naam) like '%PRORAIL%')""",
                """CREATE VIEW brk_eigenaar_niet_natuurlijk AS SELECT 9 as cat_id, 'Overig niet natuurlijk'::varchar as categorie, ks.* from brk_kadastraalsubject ks
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
                "DROP TABLE IF EXISTS brk_eigenaarcategorie",
                "DROP TABLE IF EXISTS brk_eigenaar",
                "DROP TABLE IF EXISTS brk_bebouwde_g_percelen",
                "DROP TABLE IF EXISTS brk_bebouwde_a_percelen",
                "DROP TABLE IF EXISTS brk_eigendom",
                """create table brk_eigenaar
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
                """create table brk_eigenaarcategorie
               as
                       select cat_id id, categorie from brk_eigenaar group by 1, 2 order by 1""",
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
               WHERE kadastraal_object_id in (select id from brk_kadastraalobject where indexletter='G')
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
               WHERE  kadastraal_object_id in (select id from brk_kadastraalobject where indexletter='A')
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
                """create table brk_eigendom
               AS
                       select zr.id, zr.kadastraal_subject_id, zr.kadastraal_object_id, zr.aard_zakelijk_recht_akr, eig.cat_id, 
                              false::boolean as grondeigenaar, false::boolean as aanschrijfbaar, false::boolean as appartementeigenaar
                     from brk_eigenaar eig, brk_zakelijkrecht zr where zr.kadastraal_subject_id = eig.id 
                       and zr.kadastraal_object_id in (select id from brk_kadastraalobject where kadastrale_gemeente_id in (select id from brk_kadastralegemeente where gemeente_id='Amsterdam'))""",
                "update brk_eigendom set grondeigenaar = true where id in (select id from brk_zakelijkrecht where aard_zakelijk_recht_id = '2' and kadastraal_object_id in (select id from brk_kadastraalobject where indexletter='G'))",
                "update brk_eigendom set aanschrijfbaar = true where id in (select id from brk_bebouwde_g_percelen where aard_zakelijk_recht_id in ('3','4','7','12','13'))",
                """update brk_eigendom set aanschrijfbaar = true where id in (select id from brk_bebouwde_g_percelen bbgp where aard_zakelijk_recht_id = '2' and kadastraal_object_id not in (
               select kadastraal_object_id from brk_bebouwde_g_percelen bbgp where bbgp.aard_zakelijk_recht_id in ('3','4','7','12','13')
       )) and aanschrijfbaar = false::boolean""",
                """update brk_eigendom set aanschrijfbaar = true where id in (select id from brk_bebouwde_g_percelen bbgp where aard_zakelijk_recht_id = '2' and kadastraal_object_id in (
               select kadastraal_object_id FROM
                       (SELECT
                               kadastraal_object_id,
                               aard_zakelijk_recht_id
                       FROM brk_bebouwde_g_percelen
                       GROUP BY 1, 2) a
                       GROUP BY 1
                       HAVING count(a.aard_zakelijk_recht_id) = 1
               )) and aanschrijfbaar = false::boolean""",
                """update brk_eigendom set appartementeigenaar = true where id in (select id from brk_bebouwde_a_percelen where aard_zakelijk_recht_id in ('3','4','7','12','13'))""",
                """update brk_eigendom set appartementeigenaar = true where id in (select id from brk_bebouwde_a_percelen bbap where aard_zakelijk_recht_id = '2' and kadastraal_object_id not in (
               select kadastraal_object_id from brk_bebouwde_a_percelen bbap where bbap.aard_zakelijk_recht_id in ('3','4','7','12','13')
       )) and appartementeigenaar = false::boolean""",
                """update brk_eigendom set appartementeigenaar = true where id in (select id from brk_bebouwde_a_percelen bbap where aard_zakelijk_recht_id = '2' and kadastraal_object_id in (
               select kadastraal_object_id FROM
                       (SELECT
                                kadastraal_object_id,
                                aard_zakelijk_recht_id
                        FROM brk_bebouwde_a_percelen
                        GROUP BY 1, 2) a
               GROUP BY 1
               HAVING count(a.aard_zakelijk_recht_id) = 1
       )) and appartementeigenaar = false::boolean""",
]
