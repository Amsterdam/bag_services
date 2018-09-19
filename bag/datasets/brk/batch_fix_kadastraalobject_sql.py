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
sql_command = """
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
         JOIN kot_g_poly ON kot_g_poly.id = kot.id        	
         WHERE vbo.geometrie IS NOT NULL AND
           (g_poly IS NULL OR ST_Within( vbo.geometrie, g_poly) = true))
UPDATE brk_kadastraalobject SET point_geom = vbo_kot_geometrie.geometrie  
FROM vbo_kot_geometrie
WHERE  brk_kadastraalobject.id = vbo_kot_geometrie.id  
 """
