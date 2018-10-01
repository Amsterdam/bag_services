sql_commands = [
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
    """
CREATE VIEW brk_eigenaar_natuurlijk AS
    SELECT 10 as cat_id
        , 'Overige natuurlijke personen'::varchar as categorie
        , ks.* from brk_kadastraalsubject ks
    WHERE ks.rechtsvorm_id is null
    """,
    """
CREATE VIEW brk_eigenaar_gemeente AS
    SELECT 1 as cat_id
        , 'Gemeente Amsterdam'::varchar as categorie
        , ks.* from brk_kadastraalsubject ks
    WHERE ks.rechtsvorm_id='10'
        AND (upper(ks.statutaire_naam) LIKE '%AMSTERDAM%' OR UPPER(ks.statutaire_naam) LIKE '%STADSDEEL%')
    """,
    """
CREATE VIEW brk_eigenaar_staat AS
    SELECT 3 as cat_id
        , 'Staat'::varchar as categorie
        , ks.* from brk_kadastraalsubject ks
    WHERE (ks.rechtsvorm_id='5' or ks.rechtsvorm_id='10') AND UPPER(ks.statutaire_naam) LIKE '%DE STAAT%'
    """,
    """
CREATE VIEW brk_eigenaar_provincie AS
    SELECT 4 as cat_id
        , 'Provincies'::varchar as categorie
        , ks.* FROM brk_kadastraalsubject ks
    WHERE ks.rechtsvorm_id='10' AND UPPER(ks.statutaire_naam) LIKE '%PROVINCIE%'
    """,
    """
CREATE VIEW brk_eigenaar_waterschap AS
    SELECT 5 as cat_id
        , 'Waterschappen'::varchar as categorie
        , ks.* from brk_kadastraalsubject ks
    WHERE ks.rechtsvorm_id='10' AND (UPPER(ks.statutaire_naam) LIKE '%WATERSCHAP%' or UPPER(ks.statutaire_naam) LIKE '%HEEMRAADSCHAP%')
    """,
    """
CREATE VIEW brk_eigenaar_overige_gemeente AS
    SELECT 2 as cat_id
        , 'Overige gemeenten'::varchar AS categorie
        , ks.* from brk_kadastraalsubject ks
    WHERE ks.rechtsvorm_id='10' AND UPPER(ks.statutaire_naam) LIKE '%GEMEENTE%' AND ks.id NOT IN (
        SELECT id FROM brk_eigenaar_gemeente
        UNION
        SELECT id FROM brk_eigenaar_staat
        UNION
        SELECT id FROM brk_eigenaar_provincie
        UNION
        SELECT id FROM brk_eigenaar_waterschap)
    """,
    """
CREATE VIEW brk_eigenaar_woningcorporatie AS
    SELECT 6 as cat_id
        , 'Woningbouwcorporaties'::varchar AS categorie
        , ks.* FROM brk_kadastraalsubject ks
    WHERE id IN ('NL.KAD.Persoon.252140640','NL.KAD.Persoon.503138989','NL.KAD.Persoon.499112361',
       'NL.KAD.Persoon.172211115','NL.KAD.Persoon.478316430','NL.KAD.Persoon.11734470','NL.KAD.Persoon.519506319',
       'NL.KAD.Persoon.462322843','NL.KAD.Persoon.422423013','NL.KAD.Persoon.122930769','NL.KAD.Persoon.122912658',
       'NL.KAD.Persoon.172035933','NL.KAD.Persoon.308371616','NL.KAD.Persoon.202352911','NL.KAD.Persoon.326155554',
       'NL.KAD.Persoon.11734470','NL.KAD.Persoon.172013595','NL.KAD.Persoon.172013435','NL.KAD.Persoon.172013404',
       'NL.KAD.Persoon.172214610','NL.KAD.Persoon.11731803','NL.KAD.Persoon.311883303','NL.KAD.Persoon.199400597',
       'NL.KAD.Persoon.252140640','NL.KAD.Persoon.402718637','NL.KAD.Persoon.198921986','NL.KAD.Persoon.260547779',
       'NL.KAD.Persoon.172206338','NL.KAD.Persoon.172211115','NL.KAD.Persoon.333687163','NL.KAD.Persoon.197114580',
       'NL.KAD.Persoon.122620316','NL.KAD.Persoon.172209052','NL.KAD.Persoon.172090014','NL.KAD.Persoon.459362889',
       'NL.KAD.Persoon.406261333','NL.KAD.Persoon.172013385','NL.KAD.Persoon.331501954','NL.KAD.Persoon.260334994',
       'NL.KAD.Persoon.184029003','NL.KAD.Persoon.197352789','NL.KAD.Persoon.172219833','NL.KAD.Persoon.172107996')
    """,
    """
CREATE VIEW brk_eigenaar_vve AS
    SELECT 7 as cat_id
          , 'Verenigingen van eigenaren'::varchar as categorie
          , ks.* from brk_kadastraalsubject ks
    WHERE (ks.rechtsvorm_id='13' OR ks.rechtsvorm_id='21')
    """,
    """
CREATE VIEW brk_eigenaar_spoorwegen AS
    SELECT 8 as cat_id
        , 'Spoorwegen/ProRail'::varchar as categorie
        , ks.* from brk_kadastraalsubject ks
    WHERE ks.rechtsvorm_id NOT IN ('13', '21', '27')
        AND (UPPER(ks.statutaire_naam) LIKE 'NS VAST%' or UPPER(ks.statutaire_naam) LIKE '%SPOORWEGEN%'
            OR UPPER(ks.statutaire_naam) LIKE '%RAILINFRA%' or upper(ks.statutaire_naam) LIKE '%PRORAIL%')
    """,
    """
CREATE VIEW brk_eigenaar_niet_natuurlijk AS
    SELECT 9 AS cat_id
        , 'Overige niet-natuurlijke personen'::varchar AS categorie
        , ks.* FROM brk_kadastraalsubject ks
    where ks.id NOT IN (
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
       )
    """,
    "DROP TABLE IF EXISTS brk_eigenaarcategorie",
    "DROP TABLE IF EXISTS brk_eigenaar",
    "DROP TABLE IF EXISTS brk_bebouwde_g_percelen",
    "DROP TABLE IF EXISTS brk_bebouwde_a_percelen",
    "DROP TABLE IF EXISTS brk_eigendom",
    """
CREATE TABLE brk_eigenaar AS
    SELECT * FROM brk_eigenaar_natuurlijk
    UNION
    SELECT * FROM brk_eigenaar_gemeente
    UNION
    SELECT * FROM brk_eigenaar_overige_gemeente
    UNION
    SELECT * FROM brk_eigenaar_staat
    UNION
    SELECT * FROM brk_eigenaar_provincie
    UNION
    SELECT * FROM brk_eigenaar_waterschap
    UNION
    SELECT * FROM brk_eigenaar_woningcorporatie
    UNION
    SELECT * FROM brk_eigenaar_vve
    UNION
    SELECT * FROM brk_eigenaar_spoorwegen
    UNION
    SELECT * FROM brk_eigenaar_niet_natuurlijk
    """,
    """
CREATE TABLE brk_eigenaarcategorie as
    SELECT cat_id id, categorie FROM brk_eigenaar GROUP BY 1, 2 ORDER by 1
    """,
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
    """
CREATE TABLE brk_bebouwde_g_percelen AS
    SELECT *
    FROM brk_zakelijkrecht
    WHERE kadastraal_object_id IN (SELECT id FROM brk_kadastraalobject WHERE indexletter='G')
      AND (kadastraal_object_id IN (SELECT kadastraal_object_id
                                    FROM brk_kadastraalobjectverblijfsobjectrelatie
                                    WHERE verblijfsobject_id IS NOT NULL)
          OR kadastraal_object_id IN (SELECT id
                                      FROM brk_kadastraalobject
                                      WHERE cultuurcode_onbebouwd_id IN ('92', '93')
                                         OR ( cultuurcode_bebouwd_id IS NOT NULL
                                            AND cultuurcode_bebouwd_id NOT IN ('', '18', '18, 34', '18, 99', '34', '34, 99', '44', '46', '94', '99')
                                      )))
    """,
    """
CREATE TABLE brk_bebouwde_a_percelen AS
    SELECT *
    FROM brk_zakelijkrecht
    WHERE  kadastraal_object_id IN (SELECT id FROM brk_kadastraalobject WHERE indexletter='A')
      AND (kadastraal_object_id IN (SELECT kadastraal_object_id
                                    FROM brk_kadastraalobjectverblijfsobjectrelatie
                                    WHERE verblijfsobject_id IS NOT NULL)
            OR kadastraal_object_id IN (SELECT id
                                        FROM brk_kadastraalobject
                                        WHERE cultuurcode_onbebouwd_id IN ('92', '93')
                                          OR ( cultuurcode_bebouwd_id IS NOT NULL
                                             AND cultuurcode_bebouwd_id NOT IN ('', '18', '18, 34', '18, 99', '34', '34, 99', '44', '46', '94', '99')
            )))
    """,
    """
CREATE TABLE brk_eigendom AS
    SELECT zr.id
        , zr.kadastraal_subject_id
        , zr.kadastraal_object_id
        , zr.aard_zakelijk_recht_akr
        , eig.cat_id
        , false::boolean AS grondeigenaar
        , false::boolean AS aanschrijfbaar
        , false::boolean AS appartementeigenaar
    FROM brk_eigenaar eig, brk_zakelijkrecht zr WHERE zr.kadastraal_subject_id = eig.id
    """,
    """
UPDATE brk_eigendom
SET grondeigenaar = true
WHERE id IN (SELECT id FROM brk_zakelijkrecht
             WHERE aard_zakelijk_recht_id = '2' AND kadastraal_object_id IN (
             SELECT id FROM brk_kadastraalobject WHERE indexletter='G'))
    """,
    """
UPDATE brk_eigendom
SET aanschrijfbaar = true
WHERE id IN (SELECT id FROM brk_bebouwde_g_percelen
             WHERE aard_zakelijk_recht_id IN ('3','4','7','12','13'))
    """,
    """
UPDATE brk_eigendom
SET aanschrijfbaar = true
WHERE id IN (SELECT id FROM brk_bebouwde_g_percelen bbgp
             WHERE aard_zakelijk_recht_id = '2' AND kadastraal_object_id NOT IN (
                SELECT kadastraal_object_id
                FROM brk_bebouwde_g_percelen bbgp
                WHERE bbgp.aard_zakelijk_recht_id in ('3','4','7','12','13')))
    AND aanschrijfbaar = false::boolean
    """,
    """
UPDATE brk_eigendom
SET aanschrijfbaar = true
WHERE id in (SELECT id from brk_bebouwde_g_percelen bbgp
            WHERE aard_zakelijk_recht_id = '2' AND kadastraal_object_id IN (
               SELECT kadastraal_object_id FROM (
                 SELECT kadastraal_object_id
                      , aard_zakelijk_recht_id
                 FROM brk_bebouwde_g_percelen
                 GROUP BY 1, 2) a
               GROUP BY 1
               HAVING COUNT(a.aard_zakelijk_recht_id) = 1
               ))
    AND aanschrijfbaar = false::boolean
    """,
    """
UPDATE brk_eigendom
SET appartementeigenaar = true
WHERE id IN (SELECT id FROM brk_bebouwde_a_percelen WHERE aard_zakelijk_recht_id IN ('3','4','7','12','13'))
    """,
    """
UPDATE brk_eigendom
SET appartementeigenaar = true
WHERE id IN (
    SELECT id
    FROM brk_bebouwde_a_percelen bbap
    WHERE aard_zakelijk_recht_id = '2'
      AND kadastraal_object_id NOT IN (
          SELECT kadastraal_object_id FROM brk_bebouwde_a_percelen bbap WHERE bbap.aard_zakelijk_recht_id in ('3','4','7','12','13')
       ))
  AND appartementeigenaar = false::boolean
    """,
    """
UPDATE brk_eigendom
SET appartementeigenaar = true
WHERE id IN (
    SELECT id
    FROM brk_bebouwde_a_percelen bbap
    WHERE aard_zakelijk_recht_id = '2'
      AND kadastraal_object_id IN (
          SELECT kadastraal_object_id
          FROM (
            SELECT kadastraal_object_id
                 , aard_zakelijk_recht_id
            FROM brk_bebouwde_a_percelen
            GROUP BY 1, 2) a
          GROUP BY 1
          HAVING count(a.aard_zakelijk_recht_id) = 1 ))
  AND appartementeigenaar = false::boolean
    """,
]