# This SQL statement updates the point_geom for brk_kadastraalobject of type 'A'
# end sets it to the geometrie of the first related verblijfsobject if :
# 1) the  point_geom of the kadastraal_object is NOT in the union of related g-percelen
# 2) the geometrie of the verblijfsobject is in the  union of related g-percelen


sql_command = """
WITH kot_g_poly AS (
    SELECT id, point, g_poly FROM (	 
        SELECT kot1.id AS id, kot1.point_geom AS point, ST_Union(kot2.poly_geom) AS g_poly
        FROM brk_kadastraalobject kot1	 
        JOIN brk_aperceelgperceelrelatie ag ON ag.a_perceel_id = kot1.id	
        JOIN brk_kadastraalobject kot2 ON kot2.id =  ag.g_perceel_id
        WHERE kot1.indexletter = 'A'
        GROUP BY kot1.id, kot1.point_geom) q1
     WHERE ST_Within( point, g_poly) = false),
     vbo_kot_geometrie AS (
         SELECT distinct on(kot.id) kot.id AS id, vbo.geometrie AS geometrie
         FROM brk_kadastraalobject kot
         JOIN brk_kadastraalobjectverblijfsobjectrelatie kov ON kov.kadastraal_object_id = kot.id
         JOIN bag_verblijfsobject vbo on kov.verblijfsobject_id = vbo.id
         JOIN kot_g_poly ON kot_g_poly.id = kot.id        	
         WHERE vbo.geometrie IS NOT NULL AND ST_Within( vbo.geometrie, g_poly) = true)
UPDATE brk_kadastraalobject SET point_geom = vbo_kot_geometrie.geometrie  
FROM vbo_kot_geometrie
WHERE  brk_kadastraalobject.id = vbo_kot_geometrie.id  
 """
