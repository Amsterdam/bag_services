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
SELECT 6                                as cat_id
     , 'Woningbouwcorporaties'::varchar AS categorie
     , ks.*
FROM brk_kadastraalsubject ks
WHERE id IN (
             'NL.IMKAD.Persoon.11731803', 'NL.IMKAD.Persoon.11734470', 'NL.IMKAD.Persoon.11747036',
             'NL.IMKAD.Persoon.122620316', 'NL.IMKAD.Persoon.122912658', 'NL.IMKAD.Persoon.122930769',
             'NL.IMKAD.Persoon.146107091', 'NL.IMKAD.Persoon.146182900', 'NL.IMKAD.Persoon.172013385',
             'NL.IMKAD.Persoon.172013404', 'NL.IMKAD.Persoon.172013409', 'NL.IMKAD.Persoon.172013435',
             'NL.IMKAD.Persoon.172013441', 'NL.IMKAD.Persoon.172013454', 'NL.IMKAD.Persoon.172013482',
             'NL.IMKAD.Persoon.172013486', 'NL.IMKAD.Persoon.172013595', 'NL.IMKAD.Persoon.172013649',
             'NL.IMKAD.Persoon.172014792', 'NL.IMKAD.Persoon.172025281', 'NL.IMKAD.Persoon.172026574',
             'NL.IMKAD.Persoon.172035933', 'NL.IMKAD.Persoon.172037130', 'NL.IMKAD.Persoon.172077902',
             'NL.IMKAD.Persoon.172104184', 'NL.IMKAD.Persoon.172133521', 'NL.IMKAD.Persoon.172153866',
             'NL.IMKAD.Persoon.172206338', 'NL.IMKAD.Persoon.172211115', 'NL.IMKAD.Persoon.172219833',
             'NL.IMKAD.Persoon.184029003', 'NL.IMKAD.Persoon.184033020', 'NL.IMKAD.Persoon.197114580',
             'NL.IMKAD.Persoon.197352789', 'NL.IMKAD.Persoon.198921986', 'NL.IMKAD.Persoon.199400597',
             'NL.IMKAD.Persoon.202352911', 'NL.IMKAD.Persoon.260334994', 'NL.IMKAD.Persoon.260547779',
             'NL.IMKAD.Persoon.326155554', 'NL.IMKAD.Persoon.331501954', 'NL.IMKAD.Persoon.333687163',
             'NL.IMKAD.Persoon.402718637', 'NL.IMKAD.Persoon.421462790', 'NL.IMKAD.Persoon.462322843',
             'NL.IMKAD.Persoon.475677303', 'NL.IMKAD.Persoon.478316430', 'NL.IMKAD.Persoon.485152644',
             'NL.IMKAD.Persoon.486240372', 'NL.IMKAD.Persoon.499112361', 'NL.IMKAD.Persoon.503138989',
             'NL.IMKAD.Persoon.519506319', 'NL.IMKAD.Persoon.528141723', 'NL.IMKAD.Persoon.541400782',
             'NL.IMKAD.Persoon.557910973', 'NL.IMKAD.Persoon.571886022', 'NL.IMKAD.Persoon.252140640',
             'NL.IMKAD.Persoon.422423013', 'NL.IMKAD.Persoon.308371616', 'NL.IMKAD.Persoon.172214610',
             'NL.IMKAD.Persoon.311883303', 'NL.IMKAD.Persoon.172209052', 'NL.IMKAD.Persoon.172090014',
             'NL.IMKAD.Persoon.459362889', 'NL.IMKAD.Persoon.406261333', 'NL.IMKAD.Persoon.172107996'
    )
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
    "DROP TABLE IF EXISTS brk_erfpacht",
    # Create table brk_erfpacht by finding two zakelijkrecht relations for the same kadastraal object
    #  where one is Erfpacht (3) or Erfpacht and Opstal (13) and the other is Eigendom (2)
    # Also store if uitgegeven_door is (part) of Amsterdam or otherwise
    """
CREATE TABLE brk_erfpacht AS
SELECT zr_ei.kadastraal_object_id
	 , CASE WHEN ks.rechtsvorm_id='10'
	            AND ((UPPER(ks.statutaire_naam) LIKE '%AMSTERDAM%')
                    OR (UPPER(ks.statutaire_naam) LIKE '%STADSDEEL%')) THEN 'Amsterdam'::varchar(24)
            ELSE 'Overige'::varchar(24)
       END AS uitgegeven_door
FROM brk_zakelijkrecht zr_ei
JOIN brk_kadastraalsubject ks on zr_ei.kadastraal_subject_id = ks.id
JOIN brk_zakelijkrecht zr_ep on zr_ep.kadastraal_object_id = zr_ei.kadastraal_object_id
WHERE zr_ep.aard_zakelijk_recht_id in ('3', '13')
  AND zr_ep.aard_zakelijk_recht_akr in ('EP', 'EO')
  AND zr_ei.aard_zakelijk_recht_id = '2'
GROUP BY 1,2
    """,
]
