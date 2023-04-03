/*
    Load data from the reference database into the bag_v11 structure.

    This is a mechanism that makes legacy systems consume from data in
    the reference database in order to remove the dependency on legacy
    databases while keeping these systems alive until clients have
    migrated to the DSO-API.
    
    | REF DB                     |  BAG V11                   |
    | brk_gemeentes              |  brk_gemeente              |
    | brk_kadastralegemeentes    |  brk_kadastralegemeente    |
    | brk_kadastralegemeentecodes|  brk_kadastralegemeente    |
    | brk_kadastralesecties      |  brk_kadastralesectie      |

    Note that dimensions and primary keys between "corresponding" 
    tables are not always the same, so we need to make a case-by-case
    decision on how to map ref-db entries to the bag_v11 entries.
    These decisions are clarified below:

    Column specific mappings:
    
    * Ref-db brk_gemeentes has a temporal dimension which does not exist in bagv11:
      To remove this, we take the most recent version of the gemeente.
      Any relations pointing older versions will implicitly be dropped in the mapped data.
    * bag_v11 brk_gemeente uses naam as primary key while ref-db brk_gemeentes uses
      a temporal composite key:
      This is also solved by taking the most recent version of the gemeente
      
    General mappings:

    * spatial columns with mixed geometries are cast to their ST_Multi equivalent

*/

/* RELATIONS WITHOUT FOREIGN KEYS */
INSERT INTO 
    bag_services.brk_aardzakelijkrecht (code, omschrijving) (
        SELECT
            a.code AS code,
            a.waarde AS omschrijving
        FROM
            public.brk_aardzakelijkerechten AS a
    );


/* RELATIONS WITH FOREIGN KEYS */

/* BRK GEMEENTE */
INSERT INTO
    bag_services.brk_gemeente (gemeente, geometrie, date_modified) (
        SELECT
            attr.naam as gemeente,
            ST_Multi(attr.geometrie) as geometrie,
            now() as date_modified
        FROM
            (
                SELECT
                    identificatie,
                    MAX(volgnummer) AS mxvolgnummer
                FROM public.brk_gemeentes
                GROUP BY
                    identificatie
            ) AS unik
            INNER JOIN public.brk_gemeentes attr ON attr.identificatie = unik.identificatie
            AND unik.mxvolgnummer = attr.volgnummer
    );

/* BRK KADASTRALE GEMEENTE */
INSERT INTO
    bag_services.brk_kadastralegemeente (
        id,
        naam,
        gemeente_id,
        geometrie,
        geometrie_lines,
        date_modified
    ) (
        SELECT
            c.identificatie AS id,
            kg.identificatie AS naam,
            gm.naam AS gemeente_id,
            ST_Multi(kg.geometrie) AS geometrie,
            ST_Multi(ST_Boundary(kg.geometrie)) :: geometry(MULTILINESTRING, 28992) AS geometrie_lines,
            now() AS date_modified
        FROM
            (
                SELECT
                    identificatie,
                    MAX(volgnummer) max_volgnummer
                FROM
                    public.brk_gemeentes
                GROUP BY
                    identificatie
            ) AS g
            INNER JOIN public.brk_kadastralegemeentes kg ON g.identificatie = kg.ligt_in_gemeente_identificatie
            INNER JOIN public.brk_kadastralegemeentecodes c ON  kg.identificatie = c.is_onderdeel_van_kadastralegemeente_id
            INNER JOIN public.brk_gemeentes gm ON g.identificatie = gm.identificatie
            AND g.max_volgnummer = gm.volgnummer
    );

/* BRK KADASTRALE SECTIE */
INSERT INTO bag_services.brk_kadastralesectie (
        id,
        sectie,
        geometrie,
        geometrie_lines,
        date_modified,
        kadastrale_gemeente_id
    ) (
        SELECT
            s.identificatie AS id,
            s.code AS sectie,
            ST_Multi(s.geometrie) AS geometrie,
            ST_Multi(ST_Boundary(s.geometrie)) :: geometry(MULTILINESTRING, 28992) AS geometrie_lines,
            now() AS date_modified,
            s.is_onderdeel_van_kadastralegemeentecode_id AS kadastrale_gemeente_id
        FROM 
            public.brk_kadastralesecties AS s
            INNER JOIN public.brk_kadastralegemeentecodes AS c ON  c.identificatie = s.is_onderdeel_van_kadastralegemeentecode_id
            INNER JOIN public.brk_kadastralegemeentes AS kg ON c.is_onderdeel_van_kadastralegemeente_id = kg.identificatie
    ); /* These joins are performed to guarantee that the secties are pointing to existing kadastralegemeentecodes (FKs are not enforced in the refdb) */