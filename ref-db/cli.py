#!/usr/bin/env python
description = """
Utility for outputting SQL used to load data
from the reference database into the legacy bag_v11 database.
"""

import argparse
import logging
import sys
from typing import List

from psycopg2 import connect, sql
from psycopg2.extensions import connection as Connection

logger = logging.getLogger("refdb-loading-script")
SOURCE_SCHEMA = "public"
TARGET_SCHEMA = "bag_services"

# Select distinct entries of set of columns into a target table
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

truncate_stmt = sql.SQL("TRUNCATE {target_schema}.{target_table} CASCADE")

table_registry = {
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
    "brk_kadastraalsubject": [
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
    "brk_appartementsrechtsplitsingtype": [
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
                sql.Identifier("aard" + suffix)
                for suffix in ["_code", "_omschrijving"]
            ),
            source_schema=sql.Identifier(SOURCE_SCHEMA),
            source_table=sql.Identifier("brk_aantekeningenrechten"),
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
    default=list(table_registry),
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
