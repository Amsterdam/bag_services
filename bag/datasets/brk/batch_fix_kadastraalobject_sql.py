sql_commands = [
    # First we store the original location for A-percelen in a separate table for future reference
    # and so we can check differences.
    """
DROP TABLE IF EXISTS brk_kot_orig_diva_location
    """,
    """
CREATE TABLE brk_kot_orig_diva_location AS
SELECT id, aanduiding, point_geom
FROM brk_kadastraalobject
WHERE indexletter = 'A'
    """,
    # This SQL statement updates the point_geom for brk_kadastraalobject of type 'A'
    # end sets it to the geometrie of the first related verblijfsobject if :
    # 1) the  point_geom of the kadastraal_object is NOT in the union of related g-percelen
    # 2) the geometrie of the verblijfsobject is in the  union of related g-percelen
    #
    # The clause AND kot1.sectie_id = kot2.sectie_id was added to filter out
    # G-percelen that are not in the same sectie. These are sometimes added
    # as a error and they are the cause of very wrong locations of kadastrale objecten
    # of type A
    #
    # If for a specific kadastraalobject of type 'A' the g-percelen are not valid then
    # g-poly will be NULL. In that case the point_geometrie for was zero (because it is based on
    # G-percelen) and we can also set it by using the geometrie of verblijfsobject.
    #
    # G-percelen in the brk_aperceelgperceelrelatie are not always valid G-percelen because
    # sometimes there are multiple zakelijkrecht relations in between the A-perceel and
    # original G-perceel
    """
WITH kot_g_poly AS (
    SELECT id, g_poly FROM (
        SELECT kot1.id AS id, ST_Union(kot2.poly_geom) AS g_poly
        FROM brk_kadastraalobject kot1	 
        JOIN brk_aperceelgperceelrelatie ag ON ag.a_perceel_id = kot1.id	
        JOIN brk_kadastraalobject kot2 ON kot2.id =  ag.g_perceel_id
        WHERE kot1.indexletter = 'A'
        AND kot1.sectie_id = kot2.sectie_id
        GROUP BY kot1.id) q1),
     vbo_kot_geometrie AS (
         SELECT distinct on(kot.id) kot.id AS id, vbo.geometrie AS geometrie
         FROM brk_kadastraalobject kot
         JOIN brk_kadastraalobjectverblijfsobjectrelatie kov ON kov.kadastraal_object_id = kot.id
         JOIN bag_verblijfsobject vbo on kov.verblijfsobject_id = vbo.id
         LEFT JOIN kot_g_poly ON kot_g_poly.id = kot.id
         WHERE kot.indexletter = 'A'
            AND vbo.geometrie IS NOT NULL
            AND (g_poly IS NULL OR ST_Within( vbo.geometrie, g_poly) = true))
UPDATE brk_kadastraalobject SET point_geom = vbo_kot_geometrie.geometrie
FROM vbo_kot_geometrie
WHERE  brk_kadastraalobject.id = vbo_kot_geometrie.id  
    """,
    # Then we still have more then 3000 kadastrale objects of type 'A' without point_geom
    # We will create a new temporary table where recursive relations in brk_zakelijkrecht
    # are used to find the original G-perceel for this A-type kadastrale objecten without
    # location. This uses a improved way of determining the brk_aperceelgperceelrelatie as
    # done in brk/batch.py.  But we do not know whether brk_aperceelgperceelrelatie is used
    # elsewhere, so we use a temporary table here.
    """
CREATE TEMPORARY TABLE kot_new_geom AS
WITH RECURSIVE percelen AS (
  SELECT zr.kadastraal_object_id AS origin_id
      , _kadastraal_object_aanduiding origin_aanduiding
      , _kadastraal_object_aanduiding
      , zr.kadastraal_object_id
      , zr.betrokken_bij_id
      , zr.ontstaan_uit_id
  FROM brk_zakelijkrecht zr
  JOIN brk_kadastraalobject kot on kot.id = zr.kadastraal_object_id
  LEFT JOIN brk_kadastraalobjectverblijfsobjectrelatie kov ON kov.kadastraal_object_id = kot.id
  LEFT JOIN bag_verblijfsobject vbo on kov.verblijfsobject_id = vbo.id
  WHERE kot.indexletter = 'A'
    AND kot.point_geom IS NULL
    AND vbo.id IS NULL
  UNION
  SELECT p.origin_id
       , p.origin_aanduiding
       , z1._kadastraal_object_aanduiding
       , z1.kadastraal_object_id
       , z1.betrokken_bij_id
       , z1.ontstaan_uit_id
  FROM brk_zakelijkrecht z1, percelen p
  WHERE p.ontstaan_uit_id = z1.betrokken_bij_id
    OR p.kadastraal_object_id = z1.kadastraal_object_id
  )
SELECT percelen.origin_id AS id
     , percelen.origin_aanduiding
     , ST_Centroid(ST_Union(kot2.poly_geom)) as geometrie
FROM percelen
JOIN  brk_kadastraalobject kot2 ON kot2.id =  percelen.kadastraal_object_id
WHERE kadastraal_object_id <> origin_id
  AND kot2.indexletter = 'G'
GROUP BY percelen.origin_id, percelen.origin_aanduiding
    """,
    # The we use this temporary table to update brk_kadastraalobject point_geom for these last
    # 3000 objects
    """
UPDATE brk_kadastraalobject
SET point_geom = kot_new_geom.geometrie
FROM kot_new_geom
WHERE brk_kadastraalobject.id = kot_new_geom.id
    """,
    # Then there are still 260 kadastrale objecten without geometry. We can find a geometry for some of them
    # by looking at the recursive brk_zakelijkrecht relationsc  in both directions to other kadastrale objects of type A
    # that do have a location. This will give another 100 locations
    """
CREATE TEMPORARY TABLE kot_new_geom1 AS
WITH RECURSIVE percelen AS (
  SELECT zr.kadastraal_object_id AS origin_id
      , _kadastraal_object_aanduiding origin_aanduiding
      , _kadastraal_object_aanduiding
      , zr.kadastraal_object_id
      , zr.betrokken_bij_id
      , zr.ontstaan_uit_id
  FROM brk_zakelijkrecht zr
  JOIN brk_kadastraalobject kot on kot.id = zr.kadastraal_object_id
    WHERE kot.indexletter = 'A'
    AND kot.point_geom IS NULL
  UNION
  SELECT p.origin_id
       , p.origin_aanduiding
       , z1._kadastraal_object_aanduiding
       , z1.kadastraal_object_id
       , z1.betrokken_bij_id
       , z1.ontstaan_uit_id
  FROM brk_zakelijkrecht z1, percelen p
  WHERE (z1.ontstaan_uit_id = p.betrokken_bij_id
    OR p.ontstaan_uit_id = z1.betrokken_bij_id
    OR p.kadastraal_object_id = z1.kadastraal_object_id)
  )
SELECT distinct on (percelen.origin_id) percelen.origin_id AS id
	 , kot2.point_geom as geometrie
FROM percelen
JOIN  brk_kadastraalobject kot2 ON kot2.id =  percelen.kadastraal_object_id
WHERE kadastraal_object_id <> origin_id
 AND kot2.point_geom  IS NOT NULL
    """,
    # Use temporary table kot_new_geom1 to update point_geom
    """
UPDATE brk_kadastraalobject
SET point_geom = kot_new_geom1.geometrie
FROM kot_new_geom1
WHERE brk_kadastraalobject.id = kot_new_geom1.id
    """,
    # For the last 23 locations we look at the complex for the A-perceel. The complex
    # is identified by the aanduiding minus last 4 characters. If there is another
    # A-perceel in the complex with a location, then we also use the location for that
    # A-perceel for the missing location.
    """
CREATE TEMPORARY TABLE kot_new_geom2 AS
SELECT distinct on(kot1.id) kot1.id, kot2.point_geom
FROM brk_kadastraalobject kot1
JOIN brk_kadastraalobject kot2 on LEFT(kot1.aanduiding, -4) = LEFT(kot2.aanduiding, -4)
WHERE kot1.point_geom IS NULL
  AND kot1.indexletter = 'A'
  AND kot2.point_geom IS NOT NULL
    """,
    """
UPDATE brk_kadastraalobject
SET point_geom = kot_new_geom2.point_geom
FROM kot_new_geom2
WHERE brk_kadastraalobject.id = kot_new_geom2.id
    """,
    # Report number of changed locations
    """
DO $$DECLARE c int;
BEGIN
    SELECT COUNT(orig.id) INTO c
    FROM brk_kot_orig_diva_location orig
    JOIN brk_kadastraalobject kot on orig.id = kot.id
    WHERE NOT ST_Equals(orig.point_geom, kot.point_geom);
    RAISE NOTICE 'Changed % locations for kadastrale objecten', c;
END$$;
   """,
    # Report A-kadastrale objects without location. This should now be 0
   """
DO $$DECLARE c int;
BEGIN
    SELECT COUNT(kot.id) INTO c
    FROM brk_kadastraalobject kot
    WHERE kot.point_geom IS NULL
      AND kot.indexletter = 'A';
    RAISE NOTICE 'For % A-kadastrale objecten the location is not set', c;
END$$;
   """
]
