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
 
 Table specific mappings:

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
 
 General mappings:
 
 * spatial columns with mixed geometries are cast to their ST_Multi equivalent
"""

import argparse
import logging
import sys
from typing import List, Tuple, Dict

from psycopg2 import connect, sql
from psycopg2.extensions import connection as Connection


logger = logging.getLogger("refdb-loading-script")
SOURCE_SCHEMA = "public"
TARGET_SCHEMA = "bag_services"

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
                cte=cte.format(**kwargs),
                alias=sql.Identifier(alias),
            )
            for (alias, cte, kwargs) in ctes
        ]
    )


truncate_stmt = sql.SQL("TRUNCATE {target_schema}.{target_table} CASCADE")

# NOTE: entries in this dict literal dictate the correct loading order.
table_registry = {
    "brk_rechtsvorm": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_rechtsvorm"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("rechtsvorm" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("rechtsvorm_code"),
        ),
    ],
    "brk_geslacht": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_geslacht"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("geslacht" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("geslacht_code"),
        ),
    ],
    "brk_beschikkingsbevoegdheid": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_beschikkingsbevoegdheid"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("beschikkingsbevoegdheid" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("beschikkingsbevoegdheid_code"),
        ),
    ],
    "brk_land": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_land"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("geboorteland" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("geboorteland_code"),
        ),
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_land"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("land_waarnaar_vertrokken" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("land_waarnaar_vertrokken_code"),
        ),
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_land"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("postadres_buitenland" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("postadres_buitenland_code"),
        ),
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_land"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("woonadres_buitenland" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("woonadres_buitenland_code"),
        ),
    ],
    "brk_aanduidingnaam": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_aanduidingnaam"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("naam_gebruik" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastralesubjecten"),
            transfer_pk=sql.Identifier("naam_gebruik_code"),
        ),
    ],
    "brk_appartementsrechtssplitstype": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_appartementsrechtssplitstype"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("appartementsrechtsplitsingtype" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_zakelijkerechten"),
            transfer_pk=sql.Identifier("appartementsrechtsplitsingtype_code"),
        ),
    ],
    "brk_aardaantekening": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_aardaantekening"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("aard" + suffix) for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_aantekeningenkadastraleobjecten"),
            transfer_pk=sql.Identifier("aard_code"),
        ),
    ],
    "brk_aardzakelijkrecht": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_aardzakelijkrecht"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("aard_zakelijk_recht" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_zakelijkerechten"),
            transfer_pk=sql.Identifier("aard_zakelijk_recht_code"),
        ),
    ],
    "brk_cultuurcodebebouwd": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_cultuurcodebebouwd"),
            source_fields=sql.SQL(",").join(
                sql.Identifier(x) for x in ["code", "omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastraleobjecten_soort_cultuur_bebouwd"),
            transfer_pk=sql.Identifier("code"),
        ),
    ],
    "brk_cultuurcodeonbebouwd": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_cultuurcodeonbebouwd"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("soort_cultuur_onbebouwd" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_kadastraleobjecten"),
            transfer_pk=sql.Identifier("soort_cultuur_onbebouwd_code"),
        ),
    ],
    "brk_soortgrootte": [
        code_omschrijving_stmt.format(
            target_schema=sql.Identifier(TARGET_SCHEMA),
            target_table=sql.Identifier("brk_soortgrootte"),
            source_fields=sql.SQL(",").join(
                sql.Identifier("soort_grootte" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
        ),
    ],
    "brk_kadastraalsubject": [  # also inserts brk_adres
        sql.SQL(
            """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
        ),
    ],
    "brk_zakelijkrecht": [
        sql.SQL(
            """
            WITH newest_tenaamstellingen AS (
                SELECT
                    attr.*
                FROM
                    (
                        SELECT
                            identificatie,
                            MAX(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_tenaamstellingen
                        GROUP BY
                            identificatie
                    ) as n
                    INNER JOIN brk_tenaamstellingen attr ON n.identificatie = attr.identificatie
                    AND n.volgnummer = attr.volgnummer
            ),
            newest_zakelijkerechten AS (
                SELECT
                    attr.*
                FROM
                    (
                        SELECT
                            identificatie,
                            MAX(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_zakelijkerechten
                        GROUP BY
                            identificatie
                    ) as n
                    INNER JOIN {source_schema}.brk_zakelijkerechten attr ON n.identificatie = attr.identificatie
                    AND n.volgnummer = attr.volgnummer
            ),
            newest_kadastrale_objecten AS (
                SELECT
                    attr.*
                FROM
                    (
                        SELECT
                            identificatie,
                            MAX(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_kadastraleobjecten
                        GROUP BY
                            identificatie
                    ) as n
                    INNER JOIN {source_schema}.brk_kadastraleobjecten attr ON n.identificatie = attr.identificatie
                    AND n.volgnummer = attr.volgnummer
            )
            INSERT INTO
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
        ),
    ],
    "brk_aantekening": [
        sql.SQL(
            """
            WITH newest_aantekeningen_kadastraleobjecten AS (
                SELECT
                    attr.*
                FROM
                    (
                        SELECT
                            identificatie,
                            MAX(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_aantekeningenkadastraleobjecten
                        GROUP BY
                            identificatie
                    ) as n
                    INNER JOIN {source_schema}.brk_aantekeningenkadastraleobjecten attr ON n.identificatie = attr.identificatie
                    AND n.volgnummer = attr.volgnummer
            ),
            newest_kadastraleobjecten AS (
                SELECT
                    attr.*
                FROM
                    (
                        SELECT
                            identificatie,
                            MAX(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_kadastraleobjecten
                        GROUP BY
                            identificatie
                    ) as n
                    INNER JOIN {source_schema}.brk_kadastraleobjecten attr ON n.identificatie = attr.identificatie
                    AND n.volgnummer = attr.volgnummer
            )
            INSERT INTO
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
        )
    ],
    "brk_aperceelgperceelrelatie": [
        sql.SQL(
            """
            WITH newest_kadastraleobjecten AS (
                SELECT
                    attr.*
                FROM
                    (
                        SELECT
                            identificatie,
                            MAX(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_kadastraleobjecten
                        GROUP BY
                            identificatie
                    ) as n
                    INNER JOIN {source_schema}.brk_kadastraleobjecten attr ON n.identificatie = attr.identificatie
                    AND n.volgnummer = attr.volgnummer
            )
            INSERT INTO
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
        )
    ],
    "bag_gemeente": [
        sql.SQL(
            """
            WITH newest_gemeentes AS (
                SELECT
                    attr.*
                FROM
                    {source_schema}.brk_gemeentes attr
                    INNER JOIN (
                        SELECT
                            identificatie,
                            max(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.brk_gemeentes g
                        GROUP BY
                            identificatie
                    ) AS newest ON newest.identificatie = attr.identificatie
                    AND newest.volgnummer = attr.volgnummer
            )
            INSERT INTO
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
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
        )
    ],
    "bag_stadsdeel": [
        sql.SQL(
            """
            WITH newest_stadsdelen AS (
                SELECT
                    attr.*
                FROM
                    {source_schema}.gebieden_stadsdelen attr
                    INNER JOIN (
                        SELECT
                            identificatie,
                            max(volgnummer) AS volgnummer
                        FROM
                            {source_schema}.gebieden_stadsdelen g
                        GROUP BY
                            identificatie
                    ) AS newest ON newest.identificatie = attr.identificatie
                    AND newest.volgnummer = attr.volgnummer
                WHERE
                    attr.eind_geldigheid IS NULL
                    OR attr.eind_geldigheid >= NOW()
            )
            INSERT INTO
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
                        NULL AS vervallen,
                        /* hardcoded to null in legacy ETL */
                        begin_geldigheid AS ingang_cyclus,
                        /* set like this in legacy ETL */
                        documentnummer AS brondocument_naam,
                        documentdatum AS brondocument_datum
                    FROM
                        newest_stadsdelen
                );
        """
        ).format(
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
                        NULL AS vervallen,
                        /*hardcoded in legacy ETL*/
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
                            "schema": sql.Identifier(SOURCE_SCHEMA),
                        },
                    ),
                    (
                        "nw",
                        extract_newest_stmt,
                        {
                            "table": sql.Identifier("bag_woonplaatsen"),
                            "schema": sql.Identifier(SOURCE_SCHEMA),
                        },
                    ),
                ]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
                    TYPE,
                    naam,
                    naam_nen,
                    vervallen,
                    geometrie,
                    omschrijving,
                    bron_id,
                    woonplaats_id,
                    STATUS
                ) (
                    SELECT
                        nor.documentnummer AS document_nummer,
                        nor.documentdatum AS document_mutatie,
                        nor.begin_geldigheid AS begin_geldigheid,
                        nor.eind_geldigheid AS einde_geldigheid,
                        nor.identificatie AS id,
                        nor.identificatie AS landelijk_id,
                        NOW() AS date_modified,
                        CONCAT('0', type_code :: text) AS TYPE,
                        nor.naam AS naam,
                        nor.naam_nen AS naam_nen,
                        NULL AS vervallen,
                        /* always null in ETL */
                        st_multi(nor.geometrie) AS geometrie,
                        nor.beschrijving_naam AS omschrijving,
                        NULL AS bron_id,
                        /* always null in ETL */
                        nor.woonplaats_identificatie AS woonplaats_id,
                        nor.status_omschrijving AS STATUS
                    FROM
                        nor
                        INNER JOIN nw ON nw.identificatie = nor.ligt_in_woonplaats_identificatie
                        AND nw.volgnummer = nor.ligt_in_woonplaats_volgnummer
                        INNER JOIN ng ON nw.ligt_in_gemeente_identificatie = ng.identificatie
                        AND nw.ligt_in_gemeente_volgnummer = ng.volgummer
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
                            "schema": sql.Identifier(SOURCE_SCHEMA),
                        },
                    ),
                    (
                        "nw",
                        extract_newest_stmt,
                        {
                            "table": sql.Identifier("bag_woonplaatsen"),
                            "schema": sql.Identifier(SOURCE_SCHEMA),
                        },
                    ),
                    (
                        "nor",
                        extract_newest_stmt,
                        {
                            "table": sql.Identifier("bag_openbareruimtes"),
                            "schema": sql.Identifier(SOURCE_SCHEMA),
                        },
                    ),
                ]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            target_schema=sql.Identifier(TARGET_SCHEMA),
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
    "tables",
    nargs="*",
    help="""
        Database names of the tables in bag_v11 to generate SQL for.
        If ommitted, generate SQL for all tables.
    """,
    default=list(
        table_registry
    ),  # rely on dict insertion to guarantee the correct loading order
)
parser.add_argument(
    "--delete", help="Truncate the specified tables in bag_v11", action="store_true"
)
parser.add_argument(
    "--execute",
    help="If ommitted, only emit statements that would be executed to stdout",
    action="store_true",
)


def main(tables: List[str], connection: Connection, execute: bool, delete: bool):
    with connection.cursor() as cursor:
        for table in tables:
            if delete:
                statements = [
                    truncate_stmt.format(
                        target_table=sql.Identifier(table),
                        target_schema=sql.Identifier(TARGET_SCHEMA),
                    ),
                ]
            else:
                statements = table_registry[table]

            for statement in statements:
                if execute:
                    cursor.execute(statement)
                    logger.info("Inserted %d rows into %s", cursor.rowcount, table)
                    logger.info("status: %s", cursor.statusmessage)
                else:
                    sys.stdout.write(str(statement.as_string(cursor)))
                    sys.stdout.write("\n")


if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    with connect(
        database=args.database,
        user=args.user,
        password=args.password,
        host=args.host,
        port=args.port,
    ) as connection:
        main(args.tables, connection, args.execute, args.delete)
