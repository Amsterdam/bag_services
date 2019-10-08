"""
collect and validate bag, brk, gebieden and wkpb table counts
Version for GOB import
"""
import logging
from django.db import connection


LOG = logging.getLogger(__name__)

TABLE_TARGETS = [
    # counts override, from 22-08-2019
    (8726, 0, "bag_bouwblok"),
    (481, 0, "bag_buurt"),
    (99, 0, "bag_buurtcombinatie"),
    (22, 6, "bag_gebiedsgerichtwerken"),
    (1, 0, "bag_gemeente"),
    (48, 0, "bag_grootstedelijkgebied"),
    (2989, 0, "bag_ligplaats"),
    (524255, 0, "bag_nummeraanduiding"),
    (6293, 0, "bag_openbareruimte"),
    (184505, 0, "bag_pand"),
    (8, 0, "bag_stadsdeel"),
    (323, 0, "bag_standplaats"),
    (2, 0, "bag_unesco"),
    (518817, 0, "bag_verblijfsobject"),
    (520182, 0, "bag_verblijfsobjectpandrelatie"),
    (1, 20, "bag_woonplaats"),  # Er mogen meer woonplaatsen worden geleverd
    (4, 0, "brk_aanduidingnaam"),
    (396239, 50000, "brk_aantekening"),
    (38, 5, "brk_aardaantekening"),
    (12, 0, "brk_aardzakelijkrecht"),
    (228483, 0, "brk_adres"),
    (989428, 0, "brk_aperceelgperceelrelatie"),
    (6, 0, "brk_appartementsrechtssplitstype"),
    (8, 0, "brk_beschikkingsbevoegdheid"),
    (61, 10, "brk_cultuurcodebebouwd"),
    (27, 5, "brk_cultuurcodeonbebouwd"),
    (18, 1, "brk_gemeente"),
    (3, 0, "brk_geslacht"),
    (595405, 0, "brk_kadastraalobject"),
    (521751, 0, "brk_kadastraalobjectverblijfsobjectrelatie"),
    (348914, 0, "brk_kadastraalsubject"),
    (64, 0, "brk_kadastralegemeente"),
    (163, 0, "brk_kadastralesectie"),
    (260, 0, "brk_land"),
    (22, 10, "brk_rechtsvorm"),
    (9, 20, "brk_soortgrootte"),  # Kadaster gaat nog meer soort soortgroottes opleveren
    (936670, 0, "brk_zakelijkrecht"),
    (872015, 0, "brk_zakelijkrechtverblijfsobjectrelatie"),
    (5437, 0, "wkpb_beperking"),
    (20, 0, "wkpb_beperkingcode"),
    (321260, 0, "wkpb_beperkingkadastraalobject"),
    (338702, 0, "wkpb_beperkingverblijfsobject"),
    (6, 0, "wkpb_broncode"),
    (7731, 0, "wkpb_brondocument"),
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
