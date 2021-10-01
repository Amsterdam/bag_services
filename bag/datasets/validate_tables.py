"""
collect and validate bag, brk and gebieden table counts
Version for GOB import
"""
import logging
from django.db import connection


LOG = logging.getLogger(__name__)

TABLE_TARGETS = [
    # counts override, from 22-08-2019
    (9384, 520, "bag_bouwblok"), # Temporary allow a bigger margin, until Bouwblokken Weesp are finished
    (500, 0, "bag_buurt"),
    (110, 11, "bag_buurtcombinatie"),  # Temporary allow a bigger margin, until Weesp is added in production
    (22, 6, "bag_gebiedsgerichtwerken"),
    (2, 1, "bag_gemeente"),
    (72, 8, "bag_grootstedelijkgebied"),
    (3082, 0, "bag_ligplaats"),
    (540798, 0, "bag_nummeraanduiding"),
    (6650, 600, "bag_openbareruimte"),
    (196411, 0, "bag_pand"),
    (9, 1, "bag_stadsdeel"),  # Temporary allow a bigger margin, until Weesp is added in production
    (339, 0, "bag_standplaats"),
    (2, 0, "bag_unesco"),
    (535171, 0, "bag_verblijfsobject"),
    (536744, 0, "bag_verblijfsobjectpandrelatie"),
    (1, 20, "bag_woonplaats"),  # Er mogen meer woonplaatsen worden geleverd
    (5, 0, "brk_aanduidingnaam"),  # Temporary allow 5 possible values instead of 4
    (763500, 50000, "brk_aantekening"),
    (72, 5, "brk_aardaantekening"),
    (12, 0, "brk_aardzakelijkrecht"),
    (241614, 0, "brk_adres"),
    (1070000, 0, "brk_aperceelgperceelrelatie"), # increased value
    (7, 2, "brk_appartementsrechtssplitstype"),
    (8, 0, "brk_beschikkingsbevoegdheid"),
    (30, 10, "brk_cultuurcodebebouwd"),
    (29, 5, "brk_cultuurcodeonbebouwd"),
    (352, 1, "brk_gemeente"),
    (3, 0, "brk_geslacht"),
    (655569, 0, "brk_kadastraalobject"),
    (618682, 0, "brk_kadastraalobjectverblijfsobjectrelatie"),
    (367837, 0, "brk_kadastraalsubject"),
    (86, 0, "brk_kadastralegemeente"),
    (234, 20, "brk_kadastralesectie"),
    (266, 0, "brk_land"),
    (22, 10, "brk_rechtsvorm"),
    (10, 20, "brk_soortgrootte"),  # Kadaster gaat nog meer soort soortgroottes opleveren
    (1038235, 0, "brk_zakelijkrecht"),
    (1028629, 0, "brk_zakelijkrechtverblijfsobjectrelatie"),
]


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
               "Count ,   Target,  Deviation-Allowed,      Table,           Status \n")

    for target, override, table in table_data:
        count = sql_count(table)
        delta = abs(count - target)
        deviation = int(0.05 * target)
        if override:
            deviation = override
        if delta > deviation or count == 0:
            status = '<FAIL>'
            error = True
        else:
            status = '< OK >'

        msg = f"{count:>6} ~= {target:<11} {delta:>6}-{deviation:<6} {table:<42} {status} \n"
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

    # Count,   table
    check_table_counts(TABLE_TARGETS)
