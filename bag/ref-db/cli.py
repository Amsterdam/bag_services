#!/usr/bin/env python
description = """
Utility for outputting SQL used to load data
from the reference database into the legacy bag_v11 database.

The data transfer happens in a single transaction. Partial transfer
in separate transactions can only be done by making separate CLI
invocations with table arguments.

 Note that dimensions and primary keys between "corresponding" 
 tables are not always the same, so we need to make a case-by-case
 decision on how to map ref-db entries to the bag_v11 entries.
 These decisions are clarified below:
 
 --- BRK ---
 
 * Ref-db brk_gemeentes has a temporal dimension which does not exist in bagv11:
 To remove this, we take the most recent version of the gemeente.
 Any kadastralegemeentes pointing to older versions will implicitly be dropped in the loaded data.

 * Ref-db brk_kadastraleobjecten has a temporal dimension which does not exist in bagv11:
 To remove this, we take the most recent version of the kadastraal object.
 Zakelijke rechten and aantekeningen pointing to older versions of kadastrale objecten will
 implicitly be dropped in the loaded data.

 * bag_v11 brk_gemeente uses naam as primary key while ref-db brk_gemeentes uses
 a temporal composite key:
 This is also solved by taking the most recent version of the gemeente

 * bag_adres uses a hash of fields as primary key. To avoid primary key conflicts while loading data,
 this primary key is replaced with a generated uuid4. This may result in "duplicate" entries in the
 bag_adres table but does not produce incorrect data. Since bag_adres is not exposed as a separate entity
 in the REST API, but only as a relation via kadastraal_subject, this duplication will not leak to clients.

 * kadastraleobjecten in the ref-db support multiple cultuurcode_bebouwd_ids, bagv11 only one.
 For each row that has more than 1 we take the minimum code. This is an arbitrary decision.

 * the 'opgelegd_door' relation in the brk_aantekening table cannot be derived from the ref-db.

 * some entries in refdb brk_kadastraleobjecten geometrie column contain ST_Point geometries. These
   cannot logically be cast to polygons so we ignore these entries.

--- BAG --- 

* bag_bron, bag_gebiedsgerichtwerkenpraktijkgebieden are not loaded nor present 
  in any of the bagv11 dbs, so are ignored.
* bag_indicatieadresseerbaarobject are not loaded nor present in the dbs and also not used
    in the rest of the application
* bag_gemeente is only loaded for db compatibility with the Django app since the views
  redirect the HAL links to brk_gemeente and relations in the ref db point to brk_gemeente
* openbare ruimtes leaves less than half of the original distinct entries after the transfer. it
  is possible that this is caused by older objects being excluded.
* 5 entries are not present in refdb gebieden_grootstedelijkeprojecten: 
{'houthavens-wabo-od_od', 'koffiefabriek_gsp', 'groenehuyzen-blomwijckerpad_gsp', 'h-buurt_gsp', 'the-ox_gsp', 'ode-kavel-5a-b-en-6-wabo-od_od'}
* bag_buurten in refdb has two transitive relations (1 via wijk and 1 via ggwgebied) to bag_stadsdelen while 
  the legacy bag_buurt assumes there is 1 stadsdeel for one buurt. In the refdb, therefore, it is theoretically possible
  that a buurt resides in multiple stadsdelen. We ignore entries like this by including only buurten that reside in
  wijken en ggwgebieden that are inside the same stadsdeel.
* bag_buurten has 1 direct and 1 transitive relation to ggw_gebieden, while the legacy data assumes a single ggwgebied.
  This is solved in the same way as the previous bulletpoint.
* The following tables contain entries with different primary keys for the same names. 
  In the legacy data, these pimary keys are not present. 
  To avoid confusion, a filter on eind_geldigheid has been added to the following tables
  (the duplicates only occur in obsolete data):

    - gebieden_ggwgebieden (bag_gebiedsgerichtwerken)
    - gebieden_wijken (bag_buurtcombinatie) (here the filter is a hard requirement since all "old" codes break the <= 2 length varchar constraint)
    - gebieden_buurten (bag_buurt)
    - gebieden_bouwblokken (bag_bouwblok)

* the following denormalized fields:
    - `_gebiedsgerichtwerken_id` 
    - `_grootstedelijkproject_id`
  on tables standplaatsen, ligplaatsen and verblijfsobjecten are resolved in the legacy pipeline using an ST_Within() without 
  consideration for the scenario where the object is inside multiple polygons.
  The legacy ETL pipeline arbitrarily adds the last entry of the the ggw/ggp gebied.
  In this logic we populate these as follows:
    - `_gebiedsgerichtwerken_id` -> ggw gebied defined on the associated ggw entry
    - `_grootstedelijkproject_id` -> the first entry given by a spatial join on the gebieden_grootstedelijke_projecten table
* bag_verblijfsobject.gebruik can not be derived from ref db (?). (is:WOZ.WOB.soortObject in source data)
  
TODO: other Denormalized fields on lig/standplaats/verblijfsobj
 
 General mappings:
 
 * spatial columns with mixed geometries are cast to their ST_Multi equivalent


to be discusssed/done:
* openbare ruimtes leaves less than half of the original distinct entries after the transfer. it
  is possible that this is caused by older objects being excluded.
* brk_kadastraleobjecten, extra filter on status = 'H'
* load aantekeningen on zakelijkrechten into brk_aantekening
* if brk_kadastraleobjecten ref db geometry is of type point then load it into point_geom in bagv11
* 5 entries are not present in refdb gebieden_grootstedelijkeprojecten: 
{'houthavens-wabo-od_od', 'koffiefabriek_gsp', 'groenehuyzen-blomwijckerpad_gsp', 'h-buurt_gsp', 'the-ox_gsp', 'ode-kavel-5a-b-en-6-wabo-od_od'}
possible that they are new or that they have been added recently
* bag_buurten has 1 direct and 1 transitive relation to ggw_gebieden, while the legacy data assumes a single ggwgebied.
  This is solved in the same way as the previous bulletpoint: ggw from buurt is autoritative
* entries in all bag tables with certain statuses must be filtered out. an exhaustive list willbe provided by BenK
* bag_verblijfsobject.gebruik can not be derived from ref db (?). (is:WOZ.WOB.soortObject in source data)
  --> Can be derived from woz dataset

"""

import argparse
import logging
import sys
from typing import List, Tuple, Dict

from psycopg2 import connect, sql
from psycopg2.extensions import connection as Connection


logger = logging.getLogger("refdb-loading-script")

# Select distinct entries of a set of columns into a target table
code_omschrijving_stmt = sql.SQL(
    """
    INSERT INTO
        {target_schema}.{target_table} (code, omschrijving) (
            SELECT DISTINCT
                {source_fields}
            FROM
                {source_schema}.{source_table} t
            WHERE {transfer_pk} IS NOT NULL
            /* It is possible that what is defined as pk in bag_v11 is not a pk in the refdb */
        )
    ON CONFLICT DO NOTHING; /* It is possible that we gather duplicates from denormalized refdb tables */
"""
)

# given a table with temporal dimensions in ref-db, extract the newest entries
# it is assumed that the temporal pk is (identifier, volgnummer), which covers
# 99% of the cases
extract_newest_stmt = sql.SQL(
    """
    SELECT
        attr.*
    FROM
        {schema}.{table} attr
        INNER JOIN (
            SELECT
                identificatie,
                max(volgnummer) AS volgnummer
            FROM
                {schema}.{table}
            GROUP BY
                identificatie
        ) AS newest ON newest.identificatie = attr.identificatie
        AND newest.volgnummer = attr.volgnummer
    LIMIT {limit}
"""
)

# joins that are re-used in different INSERT queries to guarantee that joins
# are executed with the tables identical to previously loaded data.
# e.g.:
# * we load `X join Y join Z`` which produces the result set for X
# * A references X
# then we need to load A join X join Y join Z to guarantee that FK constraints are satisfied when A is loaded.
standard_joins = sql.SQL(
    """
    INNER JOIN nb ON cte.ligt_in_buurt_identificatie = nb.identificatie
    AND cte.ligt_in_buurt_volgnummer = nb.volgnummer
    INNER JOIN nw ON nb.ligt_in_wijk_identificatie = nw.identificatie
    AND nb.ligt_in_wijk_volgnummer = nw.volgnummer
    INNER JOIN nggw ON nb.ligt_in_ggwgebied_identificatie = nggw.identificatie
    AND nb.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
    AND nw.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
    AND nw.ligt_in_ggwgebied_identificatie = nggw.identificatie
    INNER JOIN ns ON nggw.ligt_in_stadsdeel_identificatie = ns.identificatie
    AND nggw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
    AND nw.ligt_in_stadsdeel_identificatie = ns.identificatie
    AND nw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
"""
)


def with_query_body(
    ctes: List[Tuple[str, sql.SQL, Dict[str, sql.Composable]]]
) -> sql.SQL:
    """Construct a WITH query body composed of the given common table
    expressions (CTEs) and corresponding aliases.

    The CTEs are supplied through a SQL object which accepts a Dict of Composables
    as formatting parameters.

    Parameters:
        * ctes: a list of tuples of (alias, cte SQL, cte SQL args)
    """
    return sql.SQL(", ").join(
        [
            sql.SQL("{alias} AS ({cte})").format(
                cte=cte.format(**{"limit": sql.Literal("ALL")} | kwargs),
                alias=sql.Identifier(alias),
            )
            for (alias, cte, kwargs) in ctes
        ]
    )


truncate_stmt = sql.SQL("TRUNCATE {target_schema}.{target_table} CASCADE")

standplaats_ligplaats_query = sql.SQL(
    """
            WITH {common_table_exprs} INSERT INTO
                {target_schema}.{target_table} (
                    document_mutatie,
                    document_nummer,
                    begin_geldigheid,
                    einde_geldigheid,
                    id,
                    date_modified,
                    landelijk_id,
                    vervallen,
                    indicatie_geconstateerd,
                    indicatie_in_onderzoek,
                    geometrie,
                    bron_id,
                    buurt_id,
                    status,
                    _openbare_ruimte_naam,
                    _huisnummer,
                    _huisletter,
                    _huisnummer_toevoeging,
                    _gebiedsgerichtwerken_id,
                    _grootstedelijkgebied_id
                ) (
                    SELECT
                        nst.documentdatum AS document_mutatie,
                        nst.documentnummer AS document_nummer,
                        nst.begin_geldigheid AS begin_geldigheid,
                        nst.eind_geldigheid AS einde_geldigheid,
                        nst.identificatie AS id,
                        NOW() AS date_modified,
                        nst.identificatie AS landelijk_id,
                        NULL AS vervallen,
                        nst.geconstateerd AS indicatie_geconstateerd,
                        (
                            CASE
                                WHEN indicaties_onderzoeken.identificatie IS NOT NULL THEN TRUE
                                ELSE FALSE
                            END
                        ) AS indicatie_in_onderzoek,
                        nst.geometrie AS geometrie,
                        /* hardcoded to null in legacy ETL */
                        NULL AS bron_id,
                        nst.ligt_in_buurt_identificatie AS buurt_id,
                        nst.status_omschrijving AS status,
                        NULL AS _openbare_ruimte_naam,
                        NULL AS _huisnummer,
                        NULL AS _huisletter,
                        NULL AS _huisnummer_toevoeging,
                        nggw.code AS _gebiedsgerichtwerken_id,
                        REPLACE(lower(ggp.naam || '_' || ggp.type), ' ', '-') AS _grootstedelijkgebied_id
                    FROM
                        nst
                        INNER JOIN nb ON nst.ligt_in_buurt_identificatie = nb.identificatie
                        AND nst.ligt_in_buurt_volgnummer = nb.volgnummer
                        INNER JOIN nw ON nb.ligt_in_wijk_identificatie = nw.identificatie
                        AND nb.ligt_in_wijk_volgnummer = nw.volgnummer
                        INNER JOIN nggw ON nb.ligt_in_ggwgebied_identificatie = nggw.identificatie
                        AND nb.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                        AND nw.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                        AND nw.ligt_in_ggwgebied_identificatie = nggw.identificatie
                        INNER JOIN ns ON nggw.ligt_in_stadsdeel_identificatie = ns.identificatie
                        AND nggw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                        AND nw.ligt_in_stadsdeel_identificatie = ns.identificatie
                        AND nw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                        LEFT JOIN indicaties_onderzoeken ON indicaties_onderzoeken.identificatie = nst.identificatie
                        AND indicaties_onderzoeken.volgnummer = nst.volgnummer
                        LEFT JOIN LATERAL (SELECT * FROM ngp WHERE ST_Contains(ngp.geometrie, nst.geometrie) LIMIT 1) ggp ON true
                );
    """
)


class TableRegistry:
    def __getitem__(self, k: str):
        return self.table_registry[k]

    def __iter__(self):
        return iter(self.table_registry)

    def __init__(self, source_schema: str, target_schema: str):
        self.source_schema = source_schema
        self.target_schema = target_schema
        # NOTE: entries in this dict literal dictate the correct loading order.
        self.table_registry = {
            "brk_rechtsvorm": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_rechtsvorm"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("rechtsvorm" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("rechtsvorm_code"),
                ),
            ],
            "brk_geslacht": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_geslacht"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("geslacht" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("geslacht_code"),
                ),
            ],
            "brk_beschikkingsbevoegdheid": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_beschikkingsbevoegdheid"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("beschikkingsbevoegdheid" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("beschikkingsbevoegdheid_code"),
                ),
            ],
            "brk_land": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_land"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("geboorteland" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("geboorteland_code"),
                ),
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_land"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("land_waarnaar_vertrokken" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("land_waarnaar_vertrokken_code"),
                ),
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_land"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("postadres_buitenland" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("postadres_buitenland_code"),
                ),
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_land"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("woonadres_buitenland" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("woonadres_buitenland_code"),
                ),
            ],
            "brk_aanduidingnaam": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_aanduidingnaam"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("naam_gebruik" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastralesubjecten"),
                    transfer_pk=sql.Identifier("naam_gebruik_code"),
                ),
            ],
            "brk_appartementsrechtssplitstype": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_appartementsrechtssplitstype"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("appartementsrechtsplitsingtype" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_zakelijkerechten"),
                    transfer_pk=sql.Identifier("appartementsrechtsplitsingtype_code"),
                ),
            ],
            "brk_aardaantekening": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_aardaantekening"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("aard" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_aantekeningenkadastraleobjecten"),
                    transfer_pk=sql.Identifier("aard_code"),
                ),
            ],
            "brk_aardzakelijkrecht": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_aardzakelijkrecht"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("aard_zakelijk_recht" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_zakelijkerechten"),
                    transfer_pk=sql.Identifier("aard_zakelijk_recht_code"),
                ),
            ],
            "brk_cultuurcodebebouwd": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_cultuurcodebebouwd"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier(x) for x in ["code", "omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier(
                        "brk_kadastraleobjecten_soort_cultuur_bebouwd"
                    ),
                    transfer_pk=sql.Identifier("code"),
                ),
            ],
            "brk_cultuurcodeonbebouwd": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_cultuurcodeonbebouwd"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("soort_cultuur_onbebouwd" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastraleobjecten"),
                    transfer_pk=sql.Identifier("soort_cultuur_onbebouwd_code"),
                ),
            ],
            "brk_soortgrootte": [
                code_omschrijving_stmt.format(
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("brk_soortgrootte"),
                    source_fields=sql.SQL(",").join(
                        sql.Identifier("soort_grootte" + suffix)
                        for suffix in ["_code", "_omschrijving"]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    source_table=sql.Identifier("brk_kadastraleobjecten"),
                    transfer_pk=sql.Identifier("soort_grootte_code"),
                ),
            ],
            "brk_gemeente": [
                sql.SQL(
                    """
                INSERT INTO
                    {target_schema}.brk_gemeente (gemeente, geometrie, date_modified) (
                        SELECT
                            attr.naam as gemeente,
                            ST_Multi(attr.geometrie) as geometrie,
                            now() as date_modified
                        FROM
                            (
                                SELECT
                                    identificatie,
                                    MAX(volgnummer) AS mxvolgnummer
                                FROM {source_schema}.brk_gemeentes
                                GROUP BY
                                    identificatie
                            ) AS unik
                            INNER JOIN {source_schema}.brk_gemeentes attr ON attr.identificatie = unik.identificatie
                            AND unik.mxvolgnummer = attr.volgnummer
                    );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                ),
            ],
            "brk_kadastralegemeente": [
                sql.SQL(
                    """
                INSERT INTO
                    {target_schema}.brk_kadastralegemeente (
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
                                    {source_schema}.brk_gemeentes
                                GROUP BY
                                    identificatie
                            ) AS g
                            INNER JOIN {source_schema}.brk_kadastralegemeentes kg ON g.identificatie = kg.ligt_in_gemeente_identificatie
                            INNER JOIN {source_schema}.brk_kadastralegemeentecodes c ON  kg.identificatie = c.is_onderdeel_van_kadastralegemeente_id
                            INNER JOIN {source_schema}.brk_gemeentes gm ON g.identificatie = gm.identificatie
                            AND g.max_volgnummer = gm.volgnummer
                    );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                ),
            ],
            "brk_kadastralesectie": [
                sql.SQL(
                    """
                INSERT INTO {target_schema}.brk_kadastralesectie (
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
                            {source_schema}.brk_kadastralesecties AS s
                            INNER JOIN {source_schema}.brk_kadastralegemeentecodes AS c ON  c.identificatie = s.is_onderdeel_van_kadastralegemeentecode_id
                            INNER JOIN {source_schema}.brk_kadastralegemeentes AS kg ON c.is_onderdeel_van_kadastralegemeente_id = kg.identificatie
                    ); /* These joins are performed to guarantee that the secties are pointing to existing kadastralegemeentecodes (FKs are not enforced in the refdb) */
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                ),
            ],
            "brk_aardzakelijkrecht": [
                sql.SQL(
                    """
                INSERT INTO 
                    {target_schema}.brk_aardzakelijkrecht (code, omschrijving) (
                        SELECT
                            a.code AS code,
                            a.waarde as omschrijving
                        FROM
                            {source_schema}.brk_aardzakelijkerechten AS a
                    );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                ),
            ],
            "brk_kadastraalsubject": [  # also inserts brk_adres
                sql.SQL(
                    """
                WITH ks_subquery AS (
                    INSERT INTO
                        {target_schema}.brk_kadastraalsubject (
                            id,
                            type,
                            date_modified,
                            voornamen,
                            voorvoegsels,
                            naam,
                            geboortedatum,
                            geboorteplaats,
                            overlijdensdatum,
                            partner_voornamen,
                            partner_voorvoegsels,
                            partner_naam,
                            rsin,
                            kvknummer,
                            statutaire_naam,
                            statutaire_zetel,
                            bron,
                            /* nonexistent in ref-db */
                            bsn,
                            aanduiding_naam_id,
                            beschikkingsbevoegdheid_id,
                            geboorteland_id,
                            geslacht_id,
                            land_waarnaar_vertrokken_id,
                            rechtsvorm_id,
                            woonadres_id,
                            postadres_id
                        ) (
                            SELECT
                                ks.identificatie AS id,
                                (
                                    CASE
                                        WHEN ks.type_subject = 'NATUURLIJK PERSOON' THEN 0
                                        ELSE 1
                                    END
                                ) AS type,
                                now() AS date_modified,
                                ks.voornamen AS voornamen,
                                ks.voorvoegsels AS voorvoegsels,
                                ks.geslachtsnaam AS naam,
                                ks.geboortedatum AS geboortedatum,
                                ks.geboorteplaats AS geboorteplaats,
                                ks.datum_overlijden AS overlijdensdatum,
                                ks.voornamen_partner AS partner_voornamen,
                                ks.voorvoegsels_partner AS partner_voorvoegsels,
                                ks.geslachtsnaam_partner AS partner_naam,
                                ks.heeft_rsin_voor AS rsin,
                                ks.heeft_kvknummer_voor AS kvknummer,
                                ks.statutaire_naam AS statutaire_naam,
                                ks.statutaire_zetel AS statutaire_zetel,
                                /* nonexistent in ref-db */
                                0 AS bron,
                                ks.heeft_bsn_voor AS bsn,
                                ks.naam_gebruik_code AS aanduiding_naam_id,
                                ks.beschikkingsbevoegdheid_code AS beschikkingsbevoegdheid_id,
                                ks.geboorteland_code AS geboorteland_id,
                                ks.geslacht_code AS geslacht_id,
                                ks.land_waarnaar_vertrokken_code AS land_waarnaar_vertrokken_id,
                                ks.rechtsvorm_code AS rechtsvorm_id,
                                CASE
                                    WHEN ks.woonadres_huisnummer is not null
                                    and ks.woonadres_postcode is not null THEN replace(uuid_generate_v4() :: text, '-', '')
                                    ELSE NULL
                                END AS woonadres_id,
                                CASE
                                    WHEN ks.postadres_huisnummer is not null
                                    and ks.postadres_postcode is not null THEN replace(uuid_generate_v4() :: text, '-', '')
                                    ELSE NULL
                                END AS postadres_id
                            FROM
                                {source_schema}.brk_kadastralesubjecten AS ks
                        ) RETURNING *
                )
                /* BRK ADRES: Note here that we dont need to DEFER the FKs by putting this into 
                a transaction because for Postgres the Common Table Expression (WITH) is part of
                the same statement as the DML below. The statement is the granularity at which
                FK-constraints are enforced by default.

                For more context, see:
                https://begriffs.com/posts/2017-08-27-deferrable-sql-constraints.html#constraint-checking-granularities
                */
                INSERT INTO
                    {target_schema}.brk_adres (
                        id,
                        openbareruimte_naam,
                        huisnummer,
                        huisletter,
                        toevoeging,
                        postcode,
                        woonplaats,
                        postbus_nummer,
                        postbus_postcode,
                        postbus_woonplaats,
                        buitenland_adres,
                        buitenland_woonplaats,
                        buitenland_regio,
                        buitenland_naam,
                        buitenland_land_id
                    ) (
                        (
                            SELECT
                                ks_subquery.woonadres_id,
                                ks.woonadres_openbare_ruimte,
                                ks.woonadres_huisnummer,
                                ks.woonadres_huisletter,
                                ks.woonadres_huisnummer_toevoeging,
                                ks.woonadres_postcode,
                                ks.woonadres_woonplaats,
                                NULL,
                                NULL,
                                NULL,
                                ks.woonadres_buitenland_adres,
                                ks.woonadres_buitenland_woonplaats,
                                ks.woonadres_buitenland_regio,
                                ks.woonadres_buitenland_naam,
                                ks.woonadres_buitenland_code
                            FROM
                                ks_subquery
                                INNER JOIN {source_schema}.brk_kadastralesubjecten ks ON ks_subquery.id = ks.identificatie
                            WHERE
                                ks.woonadres_postcode is not null
                                and ks.woonadres_huisnummer is not null
                        )
                        UNION
                        ALL (
                            SELECT
                                ks_subquery.postadres_id,
                                ks.postadres_openbare_ruimte,
                                ks.postadres_huisnummer,
                                ks.postadres_huisletter,
                                ks.postadres_huisnummer_toevoeging,
                                ks.postadres_postcode,
                                ks.postadres_woonplaats,
                                ks.postadres_postbus_nummer :: int,
                                ks.postadres_postbus_postcode,
                                ks.postadres_postbus_woonplaatsnaam,
                                ks.postadres_buitenland_adres,
                                ks.postadres_buitenland_woonplaats,
                                ks.postadres_buitenland_regio,
                                ks.postadres_buitenland_naam,
                                ks.postadres_buitenland_code
                            FROM
                                ks_subquery
                                INNER JOIN {source_schema}.brk_kadastralesubjecten ks ON ks_subquery.id = ks.identificatie
                            WHERE
                                ks.postadres_postcode is not null
                                and ks.postadres_huisnummer is not null
                        )
                    );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                ),
            ],
            "brk_kadastraalobject": [
                sql.SQL(
                    """
                    WITH codes AS (
                        SELECT
                            t.id AS id,
                            agg.parent_id AS parent_id,
                            agg.code AS code,
                            t.omschrijving AS omschrijving
                        FROM
                            (
                                SELECT
                                    parent_id,
                                    MIN(code) AS code
                                FROM
                                    {source_schema}.brk_kadastraleobjecten_soort_cultuur_bebouwd
                                GROUP BY
                                    parent_id
                            ) agg
                            INNER JOIN {source_schema}.brk_kadastraleobjecten_soort_cultuur_bebouwd t ON agg.parent_id = t.parent_id
                            AND agg.code = t.code
                    )
                    INSERT INTO
                        {target_schema}.brk_kadastraalobject (
                            id,
                            aanduiding,
                            date_modified,
                            perceelnummer,
                            indexletter,
                            indexnummer,
                            grootte,
                            koopsom,
                            koopsom_valuta_code,
                            koopjaar,
                            meer_objecten,
                            register9_tekst,
                            status_code,
                            toestandsdatum,
                            voorlopige_kadastrale_grens,
                            in_onderzoek,
                            poly_geom,
                            point_geom,
                            cultuurcode_bebouwd_id,
                            cultuurcode_onbebouwd_id,
                            kadastrale_gemeente_id,
                            sectie_id,
                            soort_grootte_id,
                            voornaamste_gerechtigde_id
                        ) (
                            SELECT
                                unik.identificatie AS id,
                                attr.kadastrale_aanduiding AS aanduiding,
                                now() AS date_modified,
                                attr.perceelnummer AS perceelnummer,
                                attr.indexletter AS indexletter,
                                attr.indexnummer AS indexnummer,
                                attr.grootte AS grootte,
                                attr.koopsom AS koopsom,
                                attr.koopsom_valutacode AS koopsom_valuta_code,
                                attr.koopjaar AS koopjaar,
                                CASE
                                    WHEN attr.indicatie_meer_objecten = 'J' THEN 1 :: boolean
                                    WHEN attr.indicatie_meer_objecten = 'N' THEN 0 :: boolean
                                    ELSE null
                                END AS meer_objecten,
                                '' AS register9_tekst,
                                /* always empty */
                                attr.status AS status_code,
                                attr.toestandsdatum AS toestandsdatum,
                                CASE
                                    WHEN attr.indicatie_voorlopige_geometrie = 'J' THEN 1 :: boolean
                                    ELSE 0 :: boolean
                                END AS voorlopige_kadastrale_grens,
                                attr.in_onderzoek AS in_onderzoek,
                                CASE
                                    WHEN ST_GeometryType(attr.geometrie) = 'ST_Polygon' 
                                    THEN ST_Multi(attr.geometrie)
                                    ELSE NULL 
                                END AS poly_geom,
                                attr.plaatscoordinaten AS point_geom,
                                codes.code AS cultuurcode_bebouwd_id,
                                attr.soort_cultuur_onbebouwd_code AS cultuurcode_onbebouwd_id,
                                attr.aangeduid_door_kadastralegemeentecode_id AS kadastrale_gemeente_id,
                                attr.aangeduid_door_kadastralesectie_id AS sectie_id,
                                attr.soort_grootte_code AS soort_grootte_id,
                                NULL AS voornaamste_gerechtigde_id
                                /* not present in refdb */
                            FROM
                                (
                                    SELECT
                                        identificatie,
                                        MAX(volgnummer) AS mxvolgnummer
                                    FROM
                                        {source_schema}.brk_kadastraleobjecten
                                    GROUP BY
                                        identificatie
                                ) AS unik
                                INNER JOIN {source_schema}.brk_kadastraleobjecten AS attr ON attr.identificatie = unik.identificatie
                                AND unik.mxvolgnummer = attr.volgnummer
                                INNER JOIN {target_schema}.brk_kadastralegemeente kg ON attr.aangeduid_door_kadastralegemeentecode_id = kg.id
                                /* exclude entries referring to "older" kadastrale_gemeentes */
                                LEFT OUTER JOIN codes ON codes.parent_id = attr.id
                        );
                    """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                ),
            ],
            "brk_zakelijkrecht": [
                sql.SQL(
                    """
                    WITH {common_table_exprs} INSERT INTO
                        {target_schema}.brk_zakelijkrecht (
                            id,
                            date_modified,
                            zrt_id,
                            aard_zakelijk_recht_akr,
                            teller,
                            noemer,
                            kadastraal_object_status,
                            _kadastraal_subject_naam,
                            _kadastraal_object_aanduiding,
                            aard_zakelijk_recht_id,
                            app_rechtsplitstype_id,
                            betrokken_bij_id,
                            kadastraal_object_id,
                            kadastraal_subject_id,
                            ontstaan_uit_id
                        ) (
                            SELECT
                                CONCAT(
                                    nz.identificatie,
                                    '-',
                                    nko.identificatie,
                                    '-',
                                    nt.identificatie
                                ) AS id,
                                now() AS date_modified,
                                nz.identificatie AS zrt_id,
                                nz.akr_aard_zakelijk_recht AS aard_zakelijk_recht_akr,
                                nt.aandeel_teller AS teller,
                                nt.aandeel_noemer AS noemer,
                                nko.status AS kadastraal_object_status,
                                CASE
                                    WHEN ks.heeft_rsin_voor IS NULL THEN CONCAT(
                                        ks.geslachtsnaam,
                                        ',',
                                        ks.voornamen,
                                        ', (',
                                        ks.geslacht_code,
                                        ')'
                                    )
                                    ELSE ks.statutaire_naam
                                END AS _kadastraal_subject_naam,
                                nko.kadastrale_aanduiding AS _kadastraal_object_aanduiding,
                                nz.aard_zakelijk_recht_code AS aard_zakelijk_recht_id,
                                nz.appartementsrechtsplitsingtype_code AS app_rechtsplitstype_id,
                                nz.betrokken_bij_apptrechtsplitsing_vve_id AS betrokken_bij_id,
                                nz.rust_op_kadastraalobject_identificatie AS kadastraal_object_id,
                                nt.van_kadastraalsubject_id AS kadastraal_subject_id,
                                nz.ontstaan_uit_apptrechtsplitsing_vve_id AS ontstaan_uit_id
                            FROM
                                newest_tenaamstellingen nt
                                INNER JOIN newest_zakelijkerechten nz ON nt.van_zakelijkrecht_identificatie = nz.identificatie
                                AND nt.van_zakelijkrecht_volgnummer = nz.volgnummer
                                INNER JOIN newest_kadastrale_objecten nko ON nz.rust_op_kadastraalobject_identificatie = nko.identificatie
                                AND nz.rust_op_kadastraalobject_volgnummer = nko.volgnummer
                                INNER JOIN {source_schema}.brk_kadastralesubjecten ks ON ks.identificatie = nt.van_kadastraalsubject_id
                        );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "newest_tenaamstellingen",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_tenaamstellingen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "newest_zakelijkerechten",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_zakelijkerechten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "newest_kadastrale_objecten",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_kadastraleobjecten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                ),
            ],
            "brk_aantekening": [
                sql.SQL(
                    """
                    WITH {common_table_exprs} INSERT INTO
                        {target_schema}.brk_aantekening (
                            aantekening_id,
                            omschrijving,
                            date_modified,
                            aard_aantekening_id,
                            kadastraal_object_id,
                            opgelegd_door_id
                        ) (
                            SELECT
                                /* id is integer sequence */
                                nak.identificatie AS aantekening_id,
                                COALESCE(nak.omschrijving, '') AS omschrijving,
                                now() AS date_modified,
                                nak.aard_code AS aard_aantekening_id,
                                nak.hft_btrk_op_kot_identificatie AS kadastraal_object_id,
                                NULL AS opgelegd_door_id
                                /* not present in refdb */
                            FROM
                                newest_aantekeningen_kadastraleobjecten nak
                                INNER JOIN newest_kadastraleobjecten nk ON nak.hft_btrk_op_kot_identificatie = nk.identificatie
                                AND nak.hft_btrk_op_kot_volgnummer = nk.volgnummer
                        );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "newest_aantekeningen_kadastraleobjecten",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier(
                                        "brk_aantekeningenkadastraleobjecten"
                                    ),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "newest_kadastraleobjecten",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_kadastraleobjecten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "brk_aperceelgperceelrelatie": [
                sql.SQL(
                    """
                    WITH {common_table_exprs} INSERT INTO
                        {target_schema}.brk_aperceelgperceelrelatie (id, g_perceel_id, a_perceel_id) (
                            SELECT
                                CONCAT(
                                    thrutable.is_ontstaan_uit_g_perceel_identificatie,
                                    '-',
                                    thrutable.kadastraleobjecten_identificatie
                                ) AS id,
                                thrutable.is_ontstaan_uit_g_perceel_identificatie,
                                thrutable.kadastraleobjecten_identificatie
                            FROM
                                newest_kadastraleobjecten AS nk
                                INNER JOIN {source_schema}.brk_kadastraleobjecten_is_ontstaan_uit_g_perceel AS thrutable ON (nk.identificatie = thrutable.is_ontstaan_uit_g_perceel_identificatie
                                AND nk.volgnummer = thrutable.is_ontstaan_uit_g_perceel_volgnummer)
                                INNER JOIN newest_kadastraleobjecten nkright ON (nkright.identificatie = thrutable.kadastraleobjecten_identificatie AND nkright.volgnummer = thrutable.kadastraleobjecten_volgnummer)
                                /* these joins happen in order to filter the m2m-table on the most recent entries */
                        );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "newest_kadastraleobjecten",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_kadastraleobjecten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_gemeente": [
                sql.SQL(
                    """
                    WITH {common_table_exprs} INSERT INTO
                        {target_schema}.bag_gemeente (
                            id,
                            code,
                            naam,
                            date_modified,
                            begin_geldigheid,
                            einde_geldigheid,
                            verzorgingsgebied,
                            vervallen
                        ) (
                            SELECT
                                identificatie AS id,
                                identificatie AS code,
                                naam AS naam,
                                NOW() AS date_modified,
                                begin_geldigheid AS begin_geldigheid,
                                eind_geldigheid AS einde_geldigheid,
                                TRUE AS verzorgingsgebied,
                                /* hardcoded in legacy batch job */
                                false AS vervallen
                                /* also hardcoded */
                            FROM
                                newest_gemeentes
                        );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "newest_gemeentes",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_gemeentes"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_stadsdeel": [
                sql.SQL(
                    """
                    WITH {common_table_exprs} INSERT INTO
                        {target_schema}.bag_stadsdeel (
                            id,
                            code,
                            naam,
                            gemeente_id,
                            date_modified,
                            begin_geldigheid,
                            einde_geldigheid,
                            geometrie,
                            vervallen,
                            ingang_cyclus,
                            brondocument_naam,
                            brondocument_datum
                        ) (
                            SELECT
                                identificatie AS id,
                                code AS code,
                                naam AS naam,
                                ligt_in_gemeente_id AS gemeente_id,
                                NOW() AS date_modified,
                                begin_geldigheid AS begin_geldigheid,
                                eind_geldigheid AS einde_geldigheid,
                                st_multi(geometrie) AS geometrie,
                                /* hardcoded to null in legacy ETL */
                                NULL AS vervallen,
                                /* set equal in legacy ETL */
                                begin_geldigheid AS ingang_cyclus,
                                documentnummer AS brondocument_naam,
                                documentdatum AS brondocument_datum
                            FROM
                                newest_stadsdelen
                        );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "newest_stadsdelen",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_woonplaats": [
                sql.SQL(
                    """
                    WITH {common_table_exprs} INSERT INTO
                        {target_schema}.bag_woonplaats (
                            document_mutatie,
                            document_nummer,
                            begin_geldigheid,
                            einde_geldigheid,
                            id,
                            date_modified,
                            landelijk_id,
                            naam,
                            vervallen,
                            gemeente_id,
                            geometrie
                        ) (
                            SELECT
                                nw.documentdatum AS document_mutatie,
                                nw.documentnummer AS document_nummer,
                                nw.begin_geldigheid AS begin_geldigheid,
                                nw.eind_geldigheid AS einde_geldigheid,
                                nw.identificatie AS id,
                                NOW() AS date_modified,
                                nw.identificatie AS landelijk_id,
                                nw.naam AS naam,
                                /* hardcoded to NULL in legacy ETL*/
                                NULL AS vervallen,
                                nw.ligt_in_gemeente_identificatie AS gemeente_id,
                                st_multi(nw.geometrie) AS geometrie
                            FROM
                                nw
                                INNER JOIN ng ON ng.identificatie = nw.ligt_in_gemeente_identificatie
                                AND ng.volgnummer = nw.ligt_in_gemeente_volgnummer
                        );
                """
                ).format(
                    common_table_exprs=with_query_body(
                        [
                            (
                                "ng",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_gemeentes"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_woonplaatsen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                )
            ],
            "bag_openbareruimte": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO
                        {target_schema}.bag_openbareruimte (
                            document_mutatie,
                            document_nummer,
                            begin_geldigheid,
                            einde_geldigheid,
                            id,
                            landelijk_id,
                            date_modified,
                            type,
                            naam,
                            naam_nen,
                            vervallen,
                            geometrie,
                            omschrijving,
                            bron_id,
                            woonplaats_id,
                            status
                        ) (
                            SELECT
                                nor.documentdatum AS document_mutatie,
                                nor.documentnummer AS document_nummer,
                                nor.begin_geldigheid AS begin_geldigheid,
                                nor.eind_geldigheid AS einde_geldigheid,
                                nor.identificatie AS id,
                                nor.identificatie AS landelijk_id,
                                NOW() AS date_modified,
                                CONCAT('0', type_code :: text) AS TYPE,
                                nor.naam AS naam,
                                nor.naam_nen AS naam_nen,
                                /* always null in ETL */
                                NULL AS vervallen,
                                st_multi(nor.geometrie) AS geometrie,
                                nor.beschrijving_naam AS omschrijving,
                                /* always null in ETL */
                                NULL AS bron_id,
                                nor.ligt_in_woonplaats_identificatie AS woonplaats_id,
                                nor.status_omschrijving AS STATUS
                            FROM
                                nor
                                INNER JOIN nw ON nw.identificatie = nor.ligt_in_woonplaats_identificatie
                                AND nw.volgnummer = nor.ligt_in_woonplaats_volgnummer
                                INNER JOIN ng ON nw.ligt_in_gemeente_identificatie = ng.identificatie
                                AND nw.ligt_in_gemeente_volgnummer = ng.volgnummer
                        );
                """
                ).format(
                    common_table_exprs=with_query_body(
                        [
                            (
                                "ng",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_gemeentes"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_woonplaatsen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nor",
                                extract_newest_stmt,
                                {
                                    "schema": sql.Identifier(source_schema),
                                    "table": sql.Identifier("bag_openbareruimtes"),
                                },
                            ),
                        ]
                    ),
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                )
            ],
            "bag_grootstedelijkgebied": [
                sql.SQL(
                    """
                    INSERT INTO
                        {target_schema}.bag_grootstedelijkgebied (
                            id,
                            naam,
                            gsg_type,
                            geometrie,
                            date_modified
                        ) (
                            SELECT
                                REPLACE(lower(naam || '_' || type), ' ', '-') AS id,
                                naam AS naam,
                                type AS gsg_type,
                                st_multi(geometrie) AS geometrie,
                                NOW() AS date_modified
                            FROM
                                {source_schema}.gebieden_grootstedelijke_projecten
                        );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                )
            ],
            "bag_gebiedsgerichtwerken": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO
                        {target_schema}.bag_gebiedsgerichtwerken (
                            id,
                            code,
                            naam,
                            date_modified,
                            geometrie,
                            stadsdeel_id
                        ) (
                            SELECT
                                newest_ggw.code AS id,
                                newest_ggw.code AS code,
                                newest_ggw.naam AS naam,
                                NOW() AS date_modified,
                                ST_Multi(newest_ggw.geometrie) AS geometrie,
                                newest_stadsdelen.identificatie AS stadsdeel_id
                            FROM
                                newest_ggw
                                INNER JOIN newest_stadsdelen ON newest_ggw.ligt_in_stadsdeel_identificatie = newest_stadsdelen.identificatie
                                AND newest_stadsdelen.volgnummer = newest_ggw.ligt_in_stadsdeel_volgnummer
                            WHERE newest_ggw.eind_geldigheid >= now() or newest_ggw.eind_geldigheid IS NULL
                        );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "newest_ggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "newest_stadsdelen",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_buurtcombinatie": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO
                        {target_schema}.bag_buurtcombinatie (
                            begin_geldigheid,
                            einde_geldigheid,
                            id,
                            naam,
                            code,
                            vollcode,
                            brondocument_naam,
                            brondocument_datum,
                            ingang_cyclus,
                            date_modified,
                            geometrie,
                            stadsdeel_id
                        ) (
                            SELECT
                                nb.begin_geldigheid AS begin_geldigheid,
                                nb.eind_geldigheid AS einde_geldigheid,
                                nb.identificatie AS id,
                                nb.naam AS naam,
                                nb.code AS code,
                                nb.code AS vollcode,
                                nb.documentnummer AS brondocument_naam,
                                nb.documentdatum AS brondocument_datum,
                                nb.begin_geldigheid AS ingang_cyclus,
                                NOW() AS date_modified,
                                ST_Multi(nb.geometrie) AS geometrie,
                                ns.identificatie AS stadsdeel_id
                            FROM
                                nb
                                INNER JOIN ns ON nb.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nb.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                            WHERE nb.eind_geldigheid IS NULL or nb.eind_geldigheid >= now()
                        );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_buurt": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO
                        {target_schema}.bag_buurt (
                            begin_geldigheid,
                            einde_geldigheid,
                            geometrie,
                            date_modified,
                            id,
                            code,
                            vollcode,
                            naam,
                            vervallen,
                            ingang_cyclus,
                            brondocument_naam,
                            brondocument_datum,
                            buurtcombinatie_id,
                            gebiedsgerichtwerken_id,
                            stadsdeel_id
                        ) (
                            SELECT
                                nb.begin_geldigheid AS begin_geldigheid,
                                nb.eind_geldigheid AS einde_geldigheid,
                                ST_Multi(nb.geometrie) AS geometrie,
                                NOW() AS date_modified,
                                nb.identificatie AS id,
                                nb.code AS code,
                                nb.code AS vollcode,
                                nb.naam AS naam,
                                NULL AS vervallen,
                                nb.begin_geldigheid AS ingang_cyclus,
                                nb.documentnummer AS brondocument_naam,
                                nb.documentdatum AS brondocument_datum,
                                nb.ligt_in_wijk_identificatie AS buurtcombinatie_id,
                                nggw.code AS gebiedsgerichtwerken_id,
                                nggw.ligt_in_stadsdeel_identificatie AS stadsdeel_id
                            FROM
                                nb
                                INNER JOIN nw ON nb.ligt_in_wijk_identificatie = nw.identificatie
                                AND nb.ligt_in_wijk_volgnummer = nw.volgnummer
                                INNER JOIN nggw ON nb.ligt_in_ggwgebied_identificatie = nggw.identificatie
                                AND nb.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                                AND nw.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                                AND nw.ligt_in_ggwgebied_identificatie = nggw.identificatie
                                INNER JOIN ns ON nggw.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nggw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                                AND nw.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                            WHERE nb.eind_geldigheid IS NULL or nb.eind_geldigheid >= now()
                        );
            """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_standplaats": [
                standplaats_ligplaats_query.format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("bag_standplaats"),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "indicaties_onderzoeken",
                                sql.SQL(
                                    """
                                    SELECT
                                        standplaatsen_identificatie AS identificatie,
                                        MAX(standplaatsen_volgnummer) AS volgnummer
                                    FROM
                                        {schema}.bag_standplaatsen_heeft_onderzoeken
                                    GROUP BY
                                        standplaatsen_identificatie
                                """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nst",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_standplaatsen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ngp",
                                sql.SQL(
                                    """SELECT
                                            type,
                                            naam, 
                                            geometrie
                                        FROM {schema}.gebieden_grootstedelijke_projecten
                                    """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_ligplaats": [
                standplaats_ligplaats_query.format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    target_table=sql.Identifier("bag_ligplaats"),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "indicaties_onderzoeken",
                                sql.SQL(
                                    """
                                    SELECT
                                        ligplaatsen_identificatie AS identificatie,
                                        MAX(ligplaatsen_volgnummer) AS volgnummer
                                    FROM
                                        {schema}.bag_ligplaatsen_heeft_onderzoeken
                                    GROUP BY
                                        ligplaatsen_identificatie
                                """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nst",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_ligplaatsen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ngp",
                                sql.SQL(
                                    """SELECT
                                            type,
                                            naam, 
                                            geometrie
                                        FROM {schema}.gebieden_grootstedelijke_projecten
                                    """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_verblijfsobject": [
                sql.SQL(
                    """
                WITH {common_table_exprs}
                    INSERT INTO
                        {target_schema}.bag_verblijfsobject (
                            document_mutatie,
                            document_nummer,
                            begin_geldigheid,
                            einde_geldigheid,
                            id,
                            date_modified,
                            landelijk_id,
                            vervallen,
                            indicatie_geconstateerd,
                            indicatie_in_onderzoek,
                            geometrie,
                            bron_id,
                            buurt_id,
                            status,
                            _openbare_ruimte_naam,
                            _huisnummer,
                            _huisletter,
                            _huisnummer_toevoeging,
                            _gebiedsgerichtwerken_id,
                            _grootstedelijkgebied_id,
                            oppervlakte,
                            verdieping_toegang,
                            aantal_eenheden_complex,
                            bouwlagen,
                            aantal_kamers,
                            gebruiksdoel_gezondheidszorgfunctie,
                            gebruiksdoel_woonfunctie,
                            hoogste_bouwlaag,
                            laagste_bouwlaag,
                            reden_afvoer,
                            reden_opvoer,
                            eigendomsverhouding,
                            gebruik,
                            gebruiksdoel,
                            toegang
                        ) (
                            SELECT
                                nst.documentdatum AS document_mutatie,
                                nst.documentnummer AS document_nummer,
                                nst.begin_geldigheid AS begin_geldigheid,
                                nst.eind_geldigheid AS einde_geldigheid,
                                nst.identificatie AS id,
                                NOW() AS date_modified,
                                nst.identificatie AS landelijk_id,
                                0 AS vervallen,
                                nst.geconstateerd AS indicatie_geconstateerd,
                                (
                                    CASE
                                        WHEN indicaties_onderzoeken.identificatie IS NOT NULL THEN TRUE
                                        ELSE FALSE
                                    END
                                ) AS indicatie_in_onderzoek,
                                nst.geometrie AS geometrie,
                                /* hardcoded to null in legacy ETL */
                                NULL AS bron_id,
                                nst.ligt_in_buurt_identificatie AS buurt_id,
                                nst.status_omschrijving AS STATUS,
                                NULL AS _openbare_ruimte_naam,
                                NULL AS _huisnummer,
                                NULL AS _huisletter,
                                NULL AS _huisnummer_toevoeging,
                                nggw.code AS _gebiedsgerichtwerken_id,
                                REPLACE(lower(ggp.naam || '_' || ggp.type), ' ', '-') AS _grootstedelijkgebied_id,
                                nst.oppervlakte AS oppervlakte,
                                nst.verdieping_toegang AS verdieping_toegang,
                                nst.aantal_eenheden_complex AS aantal_eenheden_complex,
                                nst.aantal_bouwlagen AS bouwlagen,
                                nst.aantal_kamers AS aantal_kamers,
                                nst.gebruiksdoel_gezondheidszorgfunctie_omschrijving AS gebruiksdoel_gezondheidszorgfunctie,
                                nst.gebruiksdoel_woonfunctie_omschrijving AS gebruiksdoel_woonfunctie,
                                nst.hoogste_bouwlaag AS hoogste_bouwlaag,
                                nst.laagste_bouwlaag AS laagste_bouwlaag,
                                nst.redenafvoer_omschrijving AS reden_afvoer,
                                nst.redenopvoer_omschrijving AS reden_opvoer,
                                nst.eigendomsverhouding_omschrijving AS eigendomsverhouding,
                                /* not derivable from refdb */
                                NULL AS gebruik,
                                COALESCE(gd.gebruiksdoelen, '{{}}'),
                                COALESCE(tg.toegang, '{{}}')
                            FROM
                                nst
                                INNER JOIN nb ON nst.ligt_in_buurt_identificatie = nb.identificatie
                                AND nst.ligt_in_buurt_volgnummer = nb.volgnummer
                                INNER JOIN nw ON nb.ligt_in_wijk_identificatie = nw.identificatie
                                AND nb.ligt_in_wijk_volgnummer = nw.volgnummer
                                INNER JOIN nggw ON nb.ligt_in_ggwgebied_identificatie = nggw.identificatie
                                AND nb.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                                AND nw.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                                AND nw.ligt_in_ggwgebied_identificatie = nggw.identificatie
                                INNER JOIN ns ON nggw.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nggw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                                AND nw.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                                LEFT JOIN indicaties_onderzoeken ON indicaties_onderzoeken.identificatie = nst.identificatie
                                AND indicaties_onderzoeken.volgnummer = nst.volgnummer
                                LEFT JOIN LATERAL (
                                    SELECT
                                        *
                                    FROM
                                        ngp
                                    WHERE
                                        ST_Contains(ngp.geometrie, nst.geometrie)
                                    LIMIT
                                        1
                                ) ggp ON TRUE
                                LEFT JOIN gd ON gd.parent_id = nst.id
                                LEFT JOIN tg ON tg.parent_id = nst.id
                        );

                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "indicaties_onderzoeken",
                                sql.SQL(
                                    """
                                    SELECT
                                        verblijfsobjecten_identificatie AS identificatie,
                                        MAX(verblijfsobjecten_volgnummer) AS volgnummer
                                    FROM
                                        {schema}.bag_verblijfsobjecten_heeft_onderzoeken
                                    GROUP BY
                                        verblijfsobjecten_identificatie
                                """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nst",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_verblijfsobjecten"),
                                    "schema": sql.Identifier(source_schema),
                                    "limit": sql.Literal(5000),
                                },
                            ),
                            (
                                "gd",
                                sql.SQL(
                                    """
                                    SELECT
                                        parent_id,
                                        array_agg(omschrijving) AS gebruiksdoelen
                                    FROM {schema}.bag_verblijfsobjecten_gebruiksdoel
                                    GROUP BY parent_id
                                """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "tg",
                                sql.SQL(
                                    """
                                    SELECT
                                        parent_id,
                                        array_agg(omschrijving) AS toegang
                                    FROM {schema}.bag_verblijfsobjecten_toegang
                                    GROUP BY parent_id
                                """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ngp",
                                sql.SQL(
                                    """SELECT
                                            type,
                                            naam, 
                                            geometrie
                                        FROM {schema}.gebieden_grootstedelijke_projecten
                                    """
                                ),
                                {
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_bouwblok": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO
                        {target_schema}.bag_bouwblok (
                            begin_geldigheid,
                            einde_geldigheid,
                            geometrie,
                            date_modified,
                            id,
                            code,
                            ingang_cyclus,
                            buurt_id
                        ) (
                            SELECT
                                nbb.begin_geldigheid AS begin_geldigheid,
                                nbb.eind_geldigheid AS einde_geldigheid,
                                ST_Multi(nbb.geometrie) AS geometrie,
                                NOW() AS date_modified,
                                nbb.identificatie AS id,
                                nbb.code AS code,
                                nbb.begin_geldigheid AS ingang_cyclus,
                                nb.identificatie AS buurt_id
                            FROM
                                nbb
                                INNER JOIN nb ON nbb.ligt_in_buurt_identificatie = nb.identificatie
                                AND nbb.ligt_in_buurt_volgnummer = nb.volgnummer
                                INNER JOIN nw ON nb.ligt_in_wijk_identificatie = nw.identificatie
                                AND nb.ligt_in_wijk_volgnummer = nw.volgnummer
                                INNER JOIN nggw ON nb.ligt_in_ggwgebied_identificatie = nggw.identificatie
                                AND nb.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                                AND nw.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                                AND nw.ligt_in_ggwgebied_identificatie = nggw.identificatie
                                INNER JOIN ns ON nggw.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nggw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                                AND nw.ligt_in_stadsdeel_identificatie = ns.identificatie
                                AND nw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                            WHERE nbb.eind_geldigheid IS NULL or nbb.eind_geldigheid >= now()
                        );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nbb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_bouwblokken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_pand": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO {target_schema}.bag_pand (
                        document_mutatie,
                        document_nummer,
                        begin_geldigheid,
                        einde_geldigheid,
                        id,
                        landelijk_id,
                        bouwjaar,
                        laagste_bouwlaag,
                        hoogste_bouwlaag,
                        vervallen,
                        geometrie,
                        date_modified,
                        pandnaam,
                        bouwblok_id,
                        bouwlagen,
                        ligging,
                        type_woonobject,
                        status
                    ) (
                        SELECT
                            nbp.documentdatum AS document_mutatie,
                            nbp.documentnummer AS document_nummer,
                            nbp.begin_geldigheid AS begin_geldigheid,
                            nbp.eind_geldigheid AS einde_geldigheid,
                            nbp.identificatie AS id,
                            nbp.identificatie AS landelijk_id,
                            nbp.oorspronkelijk_bouwjaar AS bouwjaar,
                            nbp.laagste_bouwlaag AS laagste_bouwlaag,
                            nbp.hoogste_bouwlaag AS hoogste_bouwlaag,
                            NULL AS vervallen,
                            ST_Multi(nbp.geometrie) AS geometrie,
                            now() AS date_modified,
                            nbp.naam AS pandnaam,
                            nbp.ligt_in_bouwblok_identificatie AS bouwblok_id,
                            nbp.aantal_bouwlagen AS bouwlagen,
                            nbp.ligging_omschrijving AS ligging,
                            nbp.type_woonobject AS type_woonobject,
                            nbp.status_omschrijving AS status
                        FROM
                            nbp
                            INNER JOIN nbb ON nbp.ligt_in_bouwblok_identificatie = nbb.identificatie
                            AND nbp.ligt_in_bouwblok_volgnummer = nbb.volgnummer
                            INNER JOIN nb ON nbb.ligt_in_buurt_identificatie = nb.identificatie
                            AND nbb.ligt_in_buurt_volgnummer = nb.volgnummer
                            INNER JOIN nw ON nb.ligt_in_wijk_identificatie = nw.identificatie
                            AND nb.ligt_in_wijk_volgnummer = nw.volgnummer
                            INNER JOIN nggw ON nb.ligt_in_ggwgebied_identificatie = nggw.identificatie
                            AND nb.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                            AND nw.ligt_in_ggwgebied_volgnummer = nggw.volgnummer
                            AND nw.ligt_in_ggwgebied_identificatie = nggw.identificatie
                            INNER JOIN ns ON nggw.ligt_in_stadsdeel_identificatie = ns.identificatie
                            AND nggw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                            AND nw.ligt_in_stadsdeel_identificatie = ns.identificatie
                            AND nw.ligt_in_stadsdeel_volgnummer = ns.volgnummer
                        WHERE nbp.eind_geldigheid IS NULL or nbp.eind_geldigheid >= now()
                    );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nbp",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_panden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nbb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_bouwblokken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_nummeraanduiding": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO {target_schema}.bag_nummeraanduiding (
                        document_mutatie,
                        document_nummer,
                        begin_geldigheid,
                        einde_geldigheid,
                        id,
                        landelijk_id,
                        huisnummer,
                        huisletter,
                        huisnummer_toevoeging,
                        postcode,
                        type,
                        vervallen,
                        date_modified,
                        bron_id,
                        ligplaats_id,
                        openbare_ruimte_id,
                        standplaats_id,
                        verblijfsobject_id,
                        type_adres,
                        status,
                        _openbare_ruimte_naam,
                        _geom
                    ) (
                        SELECT
                        nna.documentdatum AS document_mutatie,
                        nna.documentnummer AS document_nummer,
                        nna.begin_geldigheid AS begin_geldigheid,
                        nna.eind_geldigheid AS einde_geldigheid,
                        nna.identificatie AS id,
                        nna.identificatie AS landelijk_id,
                        nna.huisnummer AS huisnummer,
                        nna.huisletter AS huisletter,
                        nna.huisnummertoevoeging AS huisnummer_toevoeging,
                        nna.postcode AS postcode,
                        LPAD(nna.type_adresseerbaar_object_code::text, 2, '0') AS type,
                        NULL AS vervallen,
                        now() AS date_modified,
                        NULL AS bron_id,
                        nlg.identificatie AS ligplaats_id,
                        nor.identificatie AS openbare_ruimte_id,
                        nst.identificatie AS standplaats_id,
                        nvb.identificatie AS verblijfsobject_id,
                        nna.type_adres AS type_adres,
                        nna.status_omschrijving AS status,
                        NULL AS _openbare_ruimte_naam,
                        NULL AS _geom
                        FROM 
                            nna
                            INNER JOIN nor ON nor.identificatie = nna.ligt_aan_openbareruimte_identificatie
                            AND nor.volgnummer = nna.ligt_aan_openbareruimte_volgnummer
                            INNER JOIN nwo ON nwo.identificatie = nor.ligt_in_woonplaats_identificatie
                            AND nwo.volgnummer = nor.ligt_in_woonplaats_volgnummer
                            INNER JOIN ng ON nwo.ligt_in_gemeente_identificatie = ng.identificatie
                            AND nwo.ligt_in_gemeente_volgnummer = ng.volgnummer
                            /* FKs to standplaats, ligplaats or verblijfsobject are mutually exclusive  */
                            LEFT JOIN nst ON nst.identificatie = nna.adresseert_standplaats_identificatie
                            AND nst.volgnummer = nna.adresseert_standplaats_volgnummer
                            LEFT JOIN nlg ON nlg.identificatie = nna.adresseert_ligplaats_identificatie
                            AND nlg.volgnummer = nna.adresseert_ligplaats_volgnummer
                            LEFT JOIN nvb ON nvb.identificatie = nna.adresseert_verblijfsobject_identificatie
                            AND nvb.volgnummer = nna.adresseert_verblijfsobject_volgnummer
                        WHERE nna.eind_geldigheid IS NULL or nna.eind_geldigheid >= now()
                    );
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nna",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_nummeraanduidingen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ng",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_gemeentes"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nwo",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_woonplaatsen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nor",
                                extract_newest_stmt,
                                {
                                    "schema": sql.Identifier(source_schema),
                                    "table": sql.Identifier("bag_openbareruimtes"),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nst",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        ({newest}) AS cte
                                        {standard_joins}
                                """
                                ),
                                {
                                    "newest": extract_newest_stmt.format(
                                        schema=sql.Identifier(source_schema),
                                        table=sql.Identifier("bag_standplaatsen"),
                                    ),
                                    "standard_joins": standard_joins,
                                },
                            ),
                            (
                                "nvb",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        ({newest}) AS cte
                                        {standard_joins}
                                """
                                ),
                                {
                                    "newest": extract_newest_stmt.format(
                                        schema=sql.Identifier(source_schema),
                                        table=sql.Identifier("bag_verblijfsobjecten"),
                                    ),
                                    "standard_joins": standard_joins,
                                },
                            ),
                            (
                                "nlg",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        ({newest}) AS cte
                                        {standard_joins}
                                """
                                ),
                                {
                                    "newest": extract_newest_stmt.format(
                                        schema=sql.Identifier(source_schema),
                                        table=sql.Identifier("bag_ligplaatsen"),
                                    ),
                                    "standard_joins": standard_joins,
                                },
                            ),
                        ]
                    ),
                )
            ],
            "bag_verblijfsobjectpandrelatie": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO {target_schema}.bag_verblijfsobjectpandrelatie (
                        date_modified,
                        pand_id,
                        verblijfsobject_id
                    ) (
                        SELECT
                            NOW() AS date_modified,
                            ligt_in_panden_identificatie AS pand_id,
                            verblijfsobjecten_identificatie AS verblijfsobject_id
                        FROM 
                            nbp 
                            INNER JOIN {source_schema}.bag_verblijfsobjecten_ligt_in_panden m2m
                            ON m2m.ligt_in_panden_id = nbp.id
                            INNER JOIN nvb
                            ON m2m.verblijfsobjecten_id = nvb.id
                    )
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nbb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_bouwblokken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "bp",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("bag_panden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nbp",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        bp AS cte
                                        INNER JOIN nbb ON cte.ligt_in_bouwblok_identificatie = nbb.identificatie
                                        AND cte.ligt_in_bouwblok_volgnummer = nbb.volgnummer
                                        {standard_joins}
                                    WHERE cte.eind_geldigheid IS NULL or cte.eind_geldigheid >= now()
                                """
                                ),
                                {"standard_joins": standard_joins},
                            ),
                            (
                                "nvb",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        ({newest}) AS cte
                                        {standard_joins}
                                """
                                ),
                                {
                                    "newest": extract_newest_stmt.format(
                                        schema=sql.Identifier(source_schema),
                                        table=sql.Identifier("bag_verblijfsobjecten"),
                                    ),
                                    "standard_joins": standard_joins,
                                },
                            ),
                        ]
                    ),
                )
            ],
            "brk_kadastraalobjectverblijfsobjectrelatie": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO {target_schema}.brk_kadastraalobjectverblijfsobjectrelatie (
                        date_modified,
                        kadastraal_object_id,
                        verblijfsobject_id
                    ) (
                        SELECT
                            NOW() AS date_modified,
                            kadastraleobjecten_identificatie AS kadastraal_object_id,
                            hft_rel_mt_vot_identificatie AS verblijfsobject_id
                        FROM 
                            nvb
                            INNER JOIN {source_schema}.brk_kadastraleobjecten_hft_rel_mt_vot m2m
                            ON m2m.hft_rel_mt_vot_id = nvb.id
                            INNER JOIN nko
                            ON m2m.kadastraleobjecten_id = nko.id
                    )
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nko",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_kadastraleobjecten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nvb",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        ({newest}) AS cte
                                        {standard_joins}
                                """
                                ),
                                {
                                    "newest": extract_newest_stmt.format(
                                        schema=sql.Identifier(source_schema),
                                        table=sql.Identifier("bag_verblijfsobjecten"),
                                    ),
                                    "standard_joins": standard_joins,
                                },
                            ),
                        ]
                    ),
                )
            ],
            "brk_zakelijkrechtverblijfsobjectrelatie": [
                sql.SQL(
                    """
                    WITH {common_table_exprs}
                    INSERT INTO {target_schema}.brk_zakelijkrechtverblijfsobjectrelatie (
                        zakelijk_recht_id,
                        verblijfsobject_id
                    ) (
                        SELECT
                            nz.identificatie AS zakelijk_recht_id,
                            nvb.identificatie AS verblijfsobject_id
                        FROM 
                            nvb
                            INNER JOIN {source_schema}.brk_kadastraleobjecten_hft_rel_mt_vot m2m
                            ON m2m.hft_rel_mt_vot_id = nvb.id
                            INNER JOIN nko
                            ON m2m.kadastraleobjecten_id = nko.id
                            INNER JOIN nz
                            ON nz.rust_op_kadastraalobject_id = nko.id
                    )
                """
                ).format(
                    source_schema=sql.Identifier(source_schema),
                    target_schema=sql.Identifier(target_schema),
                    common_table_exprs=with_query_body(
                        [
                            (
                                "nko",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_kadastraleobjecten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nz",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("brk_zakelijkerechten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nb",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_buurten"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_wijken"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nggw",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_ggwgebieden"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "ns",
                                extract_newest_stmt,
                                {
                                    "table": sql.Identifier("gebieden_stadsdelen"),
                                    "schema": sql.Identifier(source_schema),
                                },
                            ),
                            (
                                "nvb",
                                sql.SQL(
                                    """
                                    SELECT 
                                        cte.* 
                                    FROM 
                                        ({newest}) AS cte
                                        {standard_joins}
                                """
                                ),
                                {
                                    "newest": extract_newest_stmt.format(
                                        schema=sql.Identifier(source_schema),
                                        table=sql.Identifier("bag_verblijfsobjecten"),
                                    ),
                                    "standard_joins": standard_joins,
                                },
                            ),
                        ]
                    ),
                )
            ],
        }


parser = argparse.ArgumentParser(description=description)
parser.add_argument("-v", "--verbose", action="store_true")

parser.add_argument("-H", "--host", default="localhost", help="db host")
parser.add_argument("-P", "--port", default="5432", help="db port")
parser.add_argument("-D", "--database", default="dataservices", help="db")
parser.add_argument("-U", "--user", default="dataservices", help="db user")
parser.add_argument("-p", "--password", default="insecure", help="db pwd")
parser.add_argument(
    "-s",
    "--source-schema",
    default="public",
    help="the schema to load refdb data from",
)
parser.add_argument(
    "-t",
    "--target-schema",
    default="bag_services",
    help="the legacy schema to load refdb data into",
)

parser.add_argument(
    "tables",
    nargs="*",
    help="""
        Database names of the tables in bag_v11 to generate SQL for.
        If ommitted, generate SQL for all tables.
    """,
)
parser.add_argument(
    "--delete", help="Truncate the specified tables in bag_v11", action="store_true"
)
parser.add_argument(
    "--execute",
    help="If ommitted, only emit statements that would be executed to stdout",
    action="store_true",
)
parser.add_argument(
    "-S",
    "--show-tables",
    help="Show bag_v11 tables and exit.",
    action="store_true",
)
parser.add_argument("search_path")


def main(
    tables: List[str],
    connection: Connection,
    execute: bool,
    delete: bool,
    table_registry: TableRegistry,
):
    with connection.cursor() as cursor:
        for table in tables:
            if delete:
                statements = [
                    truncate_stmt.format(
                        target_table=sql.Identifier(table),
                        target_schema=sql.Identifier(table_registry.target_schema),
                    ),
                ]
            else:
                statements = table_registry[table]

            n_statements = len(statements)
            for i, statement in enumerate(statements):
                if execute:
                    logger.info(
                        "Running (%d/%d) transfer for table %s", i, n_statements, table
                    )
                    cursor.execute(statement)
                    logger.info("Inserted %d rows into %s", cursor.rowcount, table)
                    logger.info("status: %s", cursor.statusmessage)
                else:
                    sys.stdout.write(str(statement.as_string(cursor)))
                    sys.stdout.write("\n")


if __name__ == "__main__":
    args = parser.parse_args()
    table_registry = TableRegistry(args.source_schema, args.target_schema)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.show_tables:
        print("\n".join(table_registry))
        sys.exit()

    with connect(
        database=args.database,
        user=args.user,
        password=args.password,
        host=args.host,
        port=args.port,
        options=f"-c search_path={args.search_path}",
    ) as connection:
        main(
            args.tables or list(table_registry),
            connection,
            args.execute,
            args.delete,
            table_registry,
        )
