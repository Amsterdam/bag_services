"""
collect and validate bag, brk, gebieden and wkpb table counts
"""
import logging
from django.db import connection


LOG = logging.getLogger(__name__)


def sql_count(table):

    count = 0

    with connection.cursor() as c:
        c.execute('SELECT COUNT(*) FROM {}'.format(connection.ops.quote_name(table)))
        row = c.fetchone()
        count += row[0]
        # LOG.debug('COUNT %-6s %s', count, table)

    return count


def check_table_counts(table_data: list):
    """
    Given list with tuples of count - table name
    check if current table counts are close
    """
    error = False
    all_msg = ("Table count errors \n"
               "Count,    Target,    Table,           Status \n")

    for target, deviation, table in table_data:
        count = sql_count(table)
        if abs(count - target) > deviation or count == 0:
            status = '<FAIL>'
            error = True
        else:
            status = '< OK >'

        msg = f"{count:>6} ~= {target:<6} {table:<42} {status} \n"
        all_msg += msg

    if error:
        LOG.error(msg)
        raise ValueError(all_msg)
    else:
        LOG.debug(all_msg)


def check_table_targets():
    """
    Check if tables have a specific count
    """
    LOG.debug('Validating table counts..')

    # Count  table
    tables_targets = [
        # counts from 15-01-2018
        # counts, allowed deviation, table
        (8597   ,  2000, "bag_bouwblok"),
        (100    ,  2000, "bag_bron"),
        (481    ,  2000, "bag_buurt"),
        (99     ,  2000, "bag_buurtcombinatie"),
        (2      ,  2000, "bag_eigendomsverhouding"),
        (19     ,  2000, "bag_financieringswijze"),
        (22     ,  2000, "bag_gebiedsgerichtwerken"),
        (320    ,  2000, "bag_gebruik"),
        (506720 ,  8000, "bag_gebruiksdoel"),
        (1      ,  2000, "bag_gemeente"),
        (27     ,  2000, "bag_grootstedelijkgebied"),
        (6      ,  2000, "bag_ligging"),
        (2921   ,  2000, "bag_ligplaats"),
        (5      ,  2000, "bag_locatieingang"),
        (519463 ,  8000, "bag_nummeraanduiding"),
        (6102   ,  2000, "bag_openbareruimte"),
        (183308 ,  2000, "bag_pand"),
        (44     ,  2000, "bag_redenafvoer"),
        (44     ,  2000, "bag_redenopvoer"),
        (8      ,  2000, "bag_stadsdeel"),
        (321    ,  2000, "bag_standplaats"),
        (43     ,  2000, "bag_status"),
        (9      ,  2000, "bag_toegang"),
        (2      ,  2000, "bag_unesco"),
        (513903 ,  9000, "bag_verblijfsobject"),
        (505141 ,  9000, "bag_verblijfsobjectpandrelatie"),
        (1      ,  2000, "bag_woonplaats"),
        (4      ,  2000, "brk_aanduidingnaam"),
        (400968 ,  40000, "brk_aantekening"),
        (32     ,  2000, "brk_aardaantekening"),
        (12     ,  2000, "brk_aardzakelijkrecht"),
        (224420 ,  5000, "brk_adres"),
        (967779 ,  9000, "brk_aperceelgperceelrelatie"),
        (6      ,  2000, "brk_appartementsrechtssplitstype"),
        (7      ,  2000, "brk_beschikkingsbevoegdheid"),
        (64     ,  2000, "brk_cultuurcodebebouwd"),
        (23     ,  2000, "brk_cultuurcodeonbebouwd"),
        (19     ,  2000, "brk_gemeente"),
        (3      ,  2000, "brk_geslacht"),
        (580221 ,  9000, "brk_kadastraalobject"),
        (518644 ,  9000, "brk_kadastraalobjectverblijfsobjectrelatie"),
        (339324 ,  9000, "brk_kadastraalsubject"),
        (66     ,  2000, "brk_kadastralegemeente"),
        (177    ,  2000, "brk_kadastralesectie"),
        (252    ,  2000, "brk_land"),
        (21     ,  2000, "brk_rechtsvorm"),
        (2      ,  2000, "brk_soortgrootte"),
        (912675 ,  9000, "brk_zakelijkrecht"),
        (877108 ,  9000, "brk_zakelijkrechtverblijfsobjectrelatie"),
        (4969   ,  2000, "wkpb_beperking"),
        (20     ,  2000, "wkpb_beperkingcode"),
        (313870 ,  5000, "wkpb_beperkingkadastraalobject"),
        (334844 ,  5000, "wkpb_beperkingverblijfsobject"),
        (6      ,  2000, "wkpb_broncode"),
        (7041   ,  2000, "wkpb_brondocument"),
    ]

    check_table_counts(tables_targets)
