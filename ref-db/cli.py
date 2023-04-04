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
            WHERE {target_pk} IS NOT NULL
            /* It is possible that what is defined as pk in bag_v11 is not a pk in the refdb */
        );
"""
)

truncate_stmt = sql.SQL("TRUNCATE {target_schema}.{target_table} CASCADE")

table_registry = {
    "brk_gemeente": sql.SQL(
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
    "brk_kadastralegemeente": sql.SQL(
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
    "brk_kadastralesectie": sql.SQL(
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
    "brk_aardzakelijkrecht": sql.SQL(
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
    "brk_rechtsvorm": code_omschrijving_stmt.format(
        target_schema=sql.Identifier(TARGET_SCHEMA),
        target_table=sql.Identifier("brk_rechtsvorm"),
        source_fields=sql.SQL(",").join(
            sql.Identifier("rechtsvorm" + suffix) for suffix in ["_code", "_omschrijving"]
        ),
        source_schema=sql.Identifier(SOURCE_SCHEMA),
        source_table=sql.Identifier("brk_kadastralesubjecten"),
        target_pk=sql.Identifier("rechtsvorm_code")
    ),
    "brk_geslacht": code_omschrijving_stmt.format(
        target_schema=sql.Identifier(TARGET_SCHEMA),
        target_table=sql.Identifier("brk_geslacht"),
        source_fields=sql.SQL(",").join(
            sql.Identifier("geslacht" + suffix) for suffix in ["_code", "_omschrijving"]
        ),
        source_schema=sql.Identifier(SOURCE_SCHEMA),
        source_table=sql.Identifier("brk_kadastralesubjecten"),
        target_pk=sql.Identifier("geslacht_code")
    ),
    "brk_beschikkingsbevoegdheid": code_omschrijving_stmt.format(
        target_schema=sql.Identifier(TARGET_SCHEMA),
        target_table=sql.Identifier("brk_beschikkingsbevoegdheid"),
        source_fields=sql.SQL(",").join(
            sql.Identifier("beschikkingsbevoegdheid" + suffix) for suffix in ["_code", "_omschrijving"]
        ),
        source_schema=sql.Identifier(SOURCE_SCHEMA),
        source_table=sql.Identifier("brk_kadastralesubjecten"),
        target_pk=sql.Identifier("beschikkingsbevoegdheid_code")
    ),
    "brk_land": code_omschrijving_stmt.format(
        target_schema=sql.Identifier(TARGET_SCHEMA),
        target_table=sql.Identifier("brk_land"),
        source_fields=sql.SQL(",").join(
            sql.Identifier("geboorteland" + suffix) for suffix in ["_code", "_omschrijving"]
        ),
        source_schema=sql.Identifier(SOURCE_SCHEMA),
        source_table=sql.Identifier("brk_kadastralesubjecten"),
        target_pk=sql.Identifier("geboorteland_code")
    ),
    "brk_aanduidingnaam": code_omschrijving_stmt.format(
        target_schema=sql.Identifier(TARGET_SCHEMA),
        target_table=sql.Identifier("brk_aanduidingnaam"),
        source_fields=sql.SQL(",").join(
            sql.Identifier("naam_gebruik" + suffix) for suffix in ["_code", "_omschrijving"]
        ),
        source_schema=sql.Identifier(SOURCE_SCHEMA),
        source_table=sql.Identifier("brk_kadastralesubjecten"),
        target_pk=sql.Identifier("naam_gebruik_code")
    ),
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
                statement = truncate_stmt.format(
                    target_table=sql.Identifier(table), target_schema=sql.Identifier(TARGET_SCHEMA)
                )
            else:
                statement = table_registry[table]

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
