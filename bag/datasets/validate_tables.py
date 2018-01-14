"""
Collect and validate bag, brk, gebieden and wkpb table counts
"""
import logging
from django.db import connection


LOG = logging.getLogger(__name__)

def sql_count(table):

    c_stmt = f"SELECT COUNT(*) FROM {table};"
    count = 0

    with connection.cursor() as c:
        c.execute(c_stmt)
        row = c.fetchone()
        count += row[0]
        LOG.debug('COUNT %-6s %s', count, table)

    return count


def check_table_counts(table_data):
    for target, table in table_data:
        count = sql_count(table)
        if count < target - 5000 and count > 0:
            LOG.debug(
                'Table Count Mismatch. %s %s is not around %s',
                table, count, target
            )
            raise ValueError()


def check_table_targets():
    """
    Check if tables have a specific count
    """
    LOG.debug('validating table counts..')

    # Count  table
    tables_targets = [
        # counts from 15-01-2018
        (8597   ,"bag_bouwblok"),
        (100    ,"bag_bron"),
        (481    ,"bag_buurt"),
        (99     ,"bag_buurtcombinatie"),
        (2      ,"bag_eigendomsverhouding"),
        (19     ,"bag_financieringswijze"),
        (22     ,"bag_gebiedsgerichtwerken"),
        (320    ,"bag_gebruik"),
        (506720 ,"bag_gebruiksdoel"),
        (1      ,"bag_gemeente"),
        (27     ,"bag_grootstedelijkgebied"),
        (6      ,"bag_ligging"),
        (2921   ,"bag_ligplaats"),
        (5      ,"bag_locatieingang"),
        (509463 ,"bag_nummeraanduiding"),
        (6102   ,"bag_openbareruimte"),
        (183308 ,"bag_pand"),
        (44     ,"bag_redenafvoer"),
        (44     ,"bag_redenopvoer"),
        (8      ,"bag_stadsdeel"),
        (321    ,"bag_standplaats"),
        (43     ,"bag_status"),
        (9      ,"bag_toegang"),
        (2      ,"bag_unesco"),
        (503903 ,"bag_verblijfsobject"),
        (505141 ,"bag_verblijfsobjectpandrelatie"),
        (1      ,"bag_woonplaats"),
        (4      ,"brk_aanduidingnaam"),
        (446968 ,"brk_aantekening"),
        (32     ,"brk_aardaantekening"),
        (12     ,"brk_aardzakelijkrecht"),
        (224420 ,"brk_adres"),
        (957779 ,"brk_aperceelgperceelrelatie"),
        (6      ,"brk_appartementsrechtssplitstype"),
        (7      ,"brk_beschikkingsbevoegdheid"),
        (64     ,"brk_cultuurcodebebouwd"),
        (23     ,"brk_cultuurcodeonbebouwd"),
        (19     ,"brk_gemeente"),
        (3      ,"brk_geslacht"),
        (580221 ,"brk_kadastraalobject"),
        (518644 ,"brk_kadastraalobjectverblijfsobjectrelatie"),
        (339324 ,"brk_kadastraalsubject"),
        (66     ,"brk_kadastralegemeente"),
        (177    ,"brk_kadastralesectie"),
        (252    ,"brk_land"),
        (21     ,"brk_rechtsvorm"),
        (2      ,"brk_soortgrootte"),
        (902675 ,"brk_zakelijkrecht"),
        (869108 ,"brk_zakelijkrechtverblijfsobjectrelatie"),
        (56     ,"django_content_type"),
        (18     ,"django_migrations"),
        (5536   ,"spatial_ref_sys"),
        (4969   ,"wkpb_beperking"),
        (20     ,"wkpb_beperkingcode"),
        (310870 ,"wkpb_beperkingkadastraalobject"),
        (334844 ,"wkpb_beperkingverblijfsobject"),
        (6      ,"wkpb_broncode"),
        (7041   ,"wkpb_brondocument"),
    ]

    check_table_counts(tables_targets)
